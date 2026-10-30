import Foundation
import AppKit

/// 无人值守跑一轮，供回归测试用（省得每次手动选文件、点按钮）。
///
/// 三种触发方式，**首选第 1 种**：
///
///     1) 直接执行包内二进制 —— 参数一定传得到，退出码还能同步拿到：
///        "高三英语作文批改.app/Contents/MacOS/EssayCorrect" \
///            --autopilot 题目.docx 作文.png [--out 输出目录]
///
///     2) defaults write com.workbuddy.essaycorrect autopilotTopic -string "/abs/题目.docx"
///        defaults write com.workbuddy.essaycorrect autopilotEssay -string "/abs/作文.png"
///        defaults write com.workbuddy.essaycorrect autopilotOut   -string "/abs/输出目录"
///        open -a "高三英语作文批改"
///
///     3) open -a "高三英语作文批改" --args --autopilot 题目.docx 作文.png [--out 目录]
///        —— **不推荐**：`open --args` 不保证能传进 `CommandLine.arguments`
///        （`--logdemo` 在 2026-10-30 踩过，本文件 2026-10-30 又踩了一次）。
///
/// 第 1 种要求 App 没在运行（`open -a` 会复用旧实例，改完代码必须 `killall EssayCorrect`）。
/// 第 2 种是兜底，也是唯一能「双击图标就替跑」的方式。
///
/// 两个位置参数都是**必填**，且各自可以用英文逗号分隔多个文件 ——
/// 作文常是 1–3 张图片（上限见 `AppState.limits(for:)`：题目 1 张、作文 3 张）。
///
/// 跑完把成品和日志复制到输出目录，然后按结果退出：
/// 0 = 成功、1 = 生成失败、2 = 超时、3 = 文件放不进上传框 / 文件不存在、4 = 双绿灯未确认。
/// 用完记得 `defaults delete` 清掉，否则下次启动还会自动跑。
enum Autopilot {

    struct Config {
        var topic: [URL]
        var essay: [URL]
        var outDir: URL
    }

    /// 整轮最长等多久（正常 1~3 分钟，留足余量）
    private static let deadline: TimeInterval = 480

    /// 等「深度思考 + 联网搜索」两个绿灯最多多久（页面慢时实测要 8~10 秒）
    private static let modeWait: TimeInterval = 60

    /// 等文件真正落进上传框最多多久（读盘 + 建缩略图是后台做的，得给点时间）
    private static let slotWait: TimeInterval = 40

    // MARK: - 解析启动参数

    /// 一个位置参数可能是 `a.png`，也可能是 `a.png,b.png`
    private static func split(_ raw: String) -> [URL] {
        raw.split(separator: ",")
            .map { $0.trimmingCharacters(in: .whitespaces) }
            .filter { !$0.isEmpty }
            .map { URL(fileURLWithPath: $0) }
    }

    static func configFromLaunch() -> Config? {
        let args = CommandLine.arguments
        if let i = args.firstIndex(of: "--autopilot"), i + 2 < args.count {
            let topic = split(args[i + 1])
            let essay = split(args[i + 2])
            guard !topic.isEmpty, !essay.isEmpty else { return nil }
            var out = topic[0].deletingLastPathComponent()
            if let j = args.firstIndex(of: "--out"), j + 1 < args.count {
                out = URL(fileURLWithPath: args[j + 1])
            }
            return Config(topic: topic, essay: essay, outDir: out)
        }

        let d = UserDefaults.standard
        guard let t = d.string(forKey: "autopilotTopic"), !t.isEmpty,
              let e = d.string(forKey: "autopilotEssay"), !e.isEmpty else { return nil }
        let topic = split(t), essay = split(e)
        guard !topic.isEmpty, !essay.isEmpty else { return nil }
        let o = d.string(forKey: "autopilotOut") ?? (t as NSString).deletingLastPathComponent
        return Config(topic: topic, essay: essay, outDir: URL(fileURLWithPath: o))
    }

    // MARK: - 主流程

    static func start(state: AppState) {
        guard let cfg = configFromLaunch() else { return }
        try? FileManager.default.createDirectory(at: cfg.outDir, withIntermediateDirectories: true)
        mark(cfg, "进入 start，题目=\(cfg.topic.map(\.lastPathComponent)) 作文=\(cfg.essay.map(\.lastPathComponent))")
        NSLog("[autopilot] 题目=%@ 作文=%@ 输出=%@",
              cfg.topic.map(\.lastPathComponent).joined(separator: ","),
              cfg.essay.map(\.lastPathComponent).joined(separator: ","),
              cfg.outDir.path)

        // 先查文件在不在。上传框**不查存在性**（它只按扩展名收卡片），
        // 不在这儿拦一道，就要等 pipeline 跑到一半才报「未能打开文件」，
        // 退出码还变成 1（生成失败），看不出其实是路径写错了。
        let missing = (cfg.topic + cfg.essay).filter { !FileManager.default.fileExists(atPath: $0.path) }
        if !missing.isEmpty {
            let names = missing.map(\.lastPathComponent).joined(separator: "、")
            finish(state: state, cfg: cfg, code: 3, note: "文件不存在：\(names)")
            return
        }

        // 给内置浏览器 3 秒把页面拉起来，先把文件塞进槽位（跟模式无关，可以先做）
        DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
            mark(cfg, "3 秒到，开始填槽")
            state.acceptBatch(cfg.topic, for: .topic)
            state.acceptBatch(cfg.essay, for: .essay)
            awaitSlots(state: state, cfg: cfg, until: Date().addingTimeInterval(slotWait))
        }
    }

    /// `acceptBatch` 是异步的（读盘、建缩略图都在后台），调完不能立刻断言成功，
    /// 得回来轮询「框里真的有东西了吗」。少了这一步，文件大的时候会误判成「放不进上传框」。
    private static func awaitSlots(state: AppState, cfg: Config, until limit: Date) {
        let topicOK = !state.items(for: .topic).isEmpty
        let essayOK = !state.items(for: .essay).isEmpty
        if topicOK && essayOK {
            mark(cfg, "两个槽已就位（题目 \(state.items(for: .topic).count) 个、作文 \(state.items(for: .essay).count) 个），等双绿灯")
            awaitModes(state: state, cfg: cfg, until: Date().addingTimeInterval(modeWait))
            return
        }
        if Date() > limit {
            let which = !topicOK && !essayOK ? "题目和作文" : (!topicOK ? "题目" : "作文")
            finish(state: state, cfg: cfg, code: 3, note: "\(which)放不进上传框")
            return
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            awaitSlots(state: state, cfg: cfg, until: limit)
        }
    }

    /// 界面上的「生成」按钮不等双绿灯也能点（模式检测失败时按钮不该永久变灰），
    /// 但无人值守必须等 —— 模式没确认就开跑，生成出来的批改稿可能没开深度思考。
    private static func awaitModes(state: AppState, cfg: Config, until limit: Date) {
        if state.modesReady {
            mark(cfg, "双绿灯已就绪，启动 pipeline")
            state.runPipeline()
            poll(state: state, cfg: cfg, until: Date().addingTimeInterval(deadline))
            return
        }
        if Date() > limit {
            finish(state: state, cfg: cfg, code: 4,
                   note: "深度思考 / 联网搜索 \(Int(modeWait)) 秒内未确认开启")
            return
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            awaitModes(state: state, cfg: cfg, until: limit)
        }
    }

    private static func poll(state: AppState, cfg: Config, until limit: Date) {
        switch state.docx {
        case .ready(let url):
            finish(state: state, cfg: cfg, code: 0, note: nil, produced: url)
        case .failed(let message):
            finish(state: state, cfg: cfg, code: 1, note: message)
        default:
            if Date() > limit {
                finish(state: state, cfg: cfg, code: 2, note: "超时")
            } else {
                DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
                    poll(state: state, cfg: cfg, until: limit)
                }
            }
        }
    }

    // MARK: - 收尾

    /// 命令行侧看不到 NSLog，把关键节点落成文件，方便判断卡在哪一步
    private static func mark(_ cfg: Config, _ note: String) {
        let url = cfg.outDir.appendingPathComponent("_trace.txt")
        let line = "\(Date())  \(note)\n"
        if let handle = try? FileHandle(forWritingTo: url) {
            handle.seekToEndOfFile()
            handle.write(Data(line.utf8))
            try? handle.close()
        } else {
            try? line.write(to: url, atomically: true, encoding: .utf8)
        }
    }

    private static func finish(state: AppState, cfg: Config, code: Int32,
                               note: String?, produced: URL? = nil) {
        let fm = FileManager.default
        try? fm.createDirectory(at: cfg.outDir, withIntermediateDirectories: true)

        if let src = produced {
            let dest = cfg.outDir.appendingPathComponent(src.lastPathComponent)
            try? fm.removeItem(at: dest)
            do {
                try fm.copyItem(at: src, to: dest)
                NSLog("[autopilot] 成品=%@", dest.path)
                mark(cfg, "成品已复制：\(dest.lastPathComponent)")
            } catch {
                NSLog("[autopilot] 复制成品失败：%@", error.localizedDescription)
                mark(cfg, "复制成品失败：\(error.localizedDescription)")
            }
        }

        let logURL = cfg.outDir.appendingPathComponent("autopilot-日志.txt")
        try? state.logText.write(to: logURL, atomically: true, encoding: .utf8)

        if let note = note {
            NSLog("[autopilot] 结束：%@", note)
            mark(cfg, "结束（退出码 \(code)）：\(note)")
        } else {
            mark(cfg, "结束（退出码 0）：成功")
        }
        exit(code)
    }
}
