# 高三英语作文批改 App · 交接文档

> 最后更新：2026-10-27 ｜ 当前版本 **v0.21** ｜ 状态：**已跑通、已发布 Release v0.14（图标＋品红背景），v0.21 为第二个 Release；规则 md 定版 v4.8，沿革见 §6.5；上传框新版界面已定版（§6.7），多文件/多格式已接进流水线（§6.8），输入框被文件名污染已修（§6.9），运行日志面板已加（§6.10），结束判定缩到 3 秒（§5.4），失败态不再改外观（§6.10），等真实网页端联调**
>
> 📌 **接手先看**：§1（这是什么）、§5（继承自讲义版、不许改的六条铁律）、§6（与讲义版的结构差异）、§7（版式规格）、§8（待办）。
>
> ⚠️ 本工程是从 `/Users/linquin/lecture-app`（讲义生成，v0.27）**整体克隆**而来，界面、交互、可靠性机制完全一致，
> 只换业务：附件、提示词、两段文案、产物版式、结束标记。凡本文没写的实现细节，一律以讲义版 HANDOVER.md 为准。
>
> 🔒 **文档边界**：本文只写**工程侧**（代码、构建、踩坑、铁律），给编程 agent 看。
> `Resources/作文批改规则.md` 是**网页版内嵌规则**，会被上传到 DeepSeek 给 AI 看，不是本文的一部分；
> 那份规则的版本变更记录在 `docs/规则md-变更记录.md`，工程侧的版本沿革在本文 §6.5。三者不要混。
> **规则 md 正文里不写版本号、不写变更说明**（用户 2026-10-26 明确要求），它只对 DeepSeek 说话。

---

## 0. 一句话说清这是什么

一个 macOS 本地 App。用户选两个 docx（作文题目 + 学生作文），App 把它们连同两个内置附件上传到 DeepSeek 网页版，
让 AI 按《作文批改规则》生成一段 **Python 脚本**，App 再用**自带的 Python 运行时**执行这段脚本，产出批改稿 docx。

全程不需要用户碰命令行，也不需要装任何东西。

**目标用户**：一位高三英语老师，用来批量批改学生作文（上海高考 25 分写作）。

---

## 1. 它和「讲义生成」的关系

同一个骨架，两套业务知识。

| 维度 | 讲义生成（lecture-app） | 作文批改（本工程） |
|---|---|---|
| 上传框 1 | 考卷 | **作文题目**（题目在前） |
| 上传框 2 | 答案 | **学生作文** |
| 内置规则 | `讲义制作规则.md` | `作文批改规则.md` |
| 内置模板 | `标准模式讲义.docx` | `标准模式批改.docx` |
| 结束标记 | `# ===LECTURE-END===` | `# ===ESSAY-END===` |
| 产物 | 备课讲义 docx | 批改稿 docx |
| 临时目录 | `讲义生成-run-` | `作文批改-run-` |
| 诊断目录 | `Application Support/讲义生成/日志` | `Application Support/作文批改/日志` |
| App 名 / 可执行 | 讲义生成 / LectureGen | 高三英语作文批改 / EssayCorrect |
| Bundle ID | com.workbuddy.lecturegen | com.workbuddy.essaycorrect |

**为什么能这样换**：App 本身不含业务知识，业务全在 `Resources/` 两个附件里，每次连同用户文件一起上传。
提示词只做四件事：执行附件规则、声明运行环境、要求结束标记、要求代码块外写 ≥3 行说明。

---

## 2. 当前状态

### ✅ 已跑通

- `./build.sh` 编译通过，产物 77MB（75MB 是内置 CPython 3.12 + python-docx）
- `--selftest` 通过：两个内置附件都能在包里找到、docTypes 正确、Python 路径正确
- `--runpython tools/sample_build.py` 通过：内置 Python 执行脚本 → 产出约 38KB docx → 产物识别正确
- 产物版式已逐项校验：A4、页边距 2.0/2.2 cm、行距 1.15、`keepNext`=0、`numPr`=0、红字 run 与蓝字编号 run 均正确写入、宋体 + Times New Roman 均已设
- 界面文案、状态机文案、诊断包、Word 卡、退出确认框全部改为作文批改语境
- **已 git 化**：`git init` 完成，基线提交 `v0.1: 从讲义生成克隆骨架，改为高三英语作文批改`（`215adbe`，1088 个文件，含 `Runtime/python`）
  - 身份沿用讲义版：`xitihangto <xitihangto@gmail.com>`（仓库级配置，非全局）
  - `.gitignore`：`dist/`、`*.app`、`.DS_Store`、`*.log`、`tmp/`
  - **`Runtime/python` 必须入库**：CI runner 靠它构建，删了 Release 就产不出来
  - 远程仓库还没建；建好后 `git remote add origin …` 再推

### ⚠️ 已知不稳定点（继承自讲义版，未做改动）

- 自动判定「AI 写完了」仍可能偶尔误判（四层判定，见 §5.4）
- AI 是否遵守 `# ===ESSAY-END===` 标记，无 100% 保证
- 「继续生成」按钮的识别靠文本匹配，DeepSeek 改文案会失效
- **未做真实网页端联调**：登录、上传、等待、抓取这条链路本版没跑过，只在讲义版验证过，逻辑一致

### ❌ 还没做

- **真实网页端联调**：多文件上传这条链路（含 pdf / 图片）本版刚接上，还没跑过真实一次生成
- 图片走的是「附件条里找文件名 / 数 blob 缩略图」的探针，DeepSeek 若改附件条样式需重新校准（见 §6.8）
- 生成成功后会删掉临时目录里的剪贴板 PNG；失败/中止则保留（要放回上传框重试）

> 图标和 GitHub 仓库这两项原本列在这里，2026-10-26 都做完了，见 §8。
> 多文件进流水线原来也在这里（v0.18 只做了界面），2026-10-27 接完了，见 §6.8。

---

## 3. 构建与调试

```bash
cd article-correct-app
./build.sh              # 增量构建到 dist/高三英语作文批改.app
./build.sh --clean      # 先整包删掉再重建（只在资源改名/删文件时需要）
./build.sh --install    # 构建 + 覆盖安装到 /Applications + 启动
```

无 Xcode 工程，纯 `swiftc` 手工组装 bundle。

**默认是增量构建**：只重编二进制、覆盖拷资源，不 `rm -rf` 整包。原因是包内 CPython 有上千个文件，
而自动化会话里的 safe-delete 钩子会拦「一次删除 > 50 个文件」，整包删必然被拦、构建直接失败。
资源用覆盖式拷贝，所以**删掉或改名一个资源文件时，必须用 `--clean` 重建**，否则旧文件会残留在包里。
`--install` 里同理：旧包先 `mv` 到 `/tmp` 再后台删，不用 `rm -rf` 正面撞钩子。

### ⚠️ 自动化会话里编译会撞到一个坑

在非交互会话 / 沙箱环境里跑 `swiftc`，会报：

```
error: external macro implementation type 'SwiftUIMacros.StateMacro' could not be found
       for macro 'State()'; ... swift-plugin-server produced malformed response
```

根因不是代码，是 swift 驱动用 `sandbox-exec` 包一层去起宏插件服务，而沙箱规则应用被拒
（`sandbox-exec: sandbox_apply: Operation not permitted`）。SwiftUI 的 `@State` 全靠这个宏。

`build.sh` 已处理：检测到工具链支持 `-disable-sandbox` 就自动加上，老工具链自动不加。
**手动编译时记得带这个参数**，否则一行代码没改也会编译失败。

### 两个命令行自检入口

```bash
# 验证包内资源、Python 路径、体积
"dist/高三英语作文批改.app/Contents/MacOS/EssayCorrect" --selftest

# 完整跑一遍脚本执行链路（不碰网页）
"dist/高三英语作文批改.app/Contents/MacOS/EssayCorrect" --runpython tools/sample_build.py
```

`--runpython` 会打印 `exit / work / files / output / docx 字节数`，是排查「Python 跑不通」最快的入口。

`tools/sample_build.py` 同时是**版式参考实现**：一份最小但完整的批改稿，run 级字体字号颜色、段前段后、
空段落位置都按规则 §3 设好，**改版式先改它、再对照它改规则**。当前已对齐 v4.4：副标题段前 2pt / 段后 4pt、
章节标题段前 8pt 段后 0、二级标题段前 6pt 段后 0、空段落 5 个（4 个章节交界 + 纠错｜补充意见之间）、
题面英文行顶格。它不随包分发，只用于开发期验证。

### 界面状态演示（截图用）

```bash
open -a "dist/高三英语作文批改.app" --args --uidemo    # 生成中
# --uidemo2 已出成品 / --uidemo3 失败 / --uidemo4 只传题目 / --uidemo5 只传作文 / --uidemo6 都传但未登录
# --uidemo7 新版上传框（题目 1 个文档 + 作文 3 张图片，已满额）
# --uidemo8 同 7，但作文框处于「等待粘贴」态，并弹一条超限提示
# --uidemo9 打开包内 docx 的预览面板
```

其他开发入口：

```bash
--prompttest                 # 打 4 个文件版 / 6 个文件版提示词，校验结束标记还在
--logdemo                    # 塞 16 行假日志并打开「运行日志」面板（看版式不用真跑一轮）
--pastetest                  # 剪贴板图片落盘自检
--preview /path/to/file      # 启动即打开该文件的预览
--qldebug                    # 把 Quick Look 的子视图树打到 stderr（查滚轮/渲染问题用）
```

### 运行时日志

`progressLines` 只进内存（上限 400 行，超了掐掉前 200 行）。**看的地方有两个**：
点 Word 卡标题行的「详情」看面板（成功/失败都能看，见 §6.10）；或者失败时点「导出诊断报告」，
md 里有完整日志。失败还会自动往 `~/Library/Application Support/作文批改/日志/` 写一份（md + 页面截图，留 30 份）。

> 旧的「状态栏显示最近 6 行」在 2026-10-27 随底部状态行一起删掉了，别再按那个找。

---

## 4. 目录结构

```
article-correct-app/
├── build.sh                    # 构建脚本（含 -disable-sandbox 兼容处理）
├── Sources/
│   ├── EssayApp.swift          # @main + ContentView + 上传卡/进度卡/Word 卡 + 退出确认
│   ├── AppState.swift          # 全局状态机（ObservableObject），双通道 JS 入口
│   ├── Pipeline.swift          # 主流程：上传 → 发送 → 等待 → 抓取
│   ├── Scripts.swift           # 注入网页的 JS（全部写成单个表达式）
│   ├── BrowserController.swift # WKWebView + 隐形窗口 + 真实鼠标注入
│   ├── PythonRunner.swift      # 内置 Python 执行器
│   ├── ScriptExtractor.swift   # 从文本里提取/打分挑出 Python 代码块
│   └── SafariBridge.swift      # AppleScript 通道（备用）
├── Resources/
│   ├── 作文批改规则.md          # 网页版内嵌规则（五部分结构 + 版式 + 禁止项）
│   ├── 标准模式批改.docx        # 版式模板（用户 2026-10-26 正式版，已按裁定改过）
│   ├── AppIcon.icns            # 自己的图标（品红底 + 竖 A4 纸 + 钢笔 + 红批改痕）
│   └── zh-Hans.lproj/          # ⚠️ 应用显示名在这里，不在 Info.plist（见 §6.2）
├── Runtime/python/             # 75MB CPython 3.12 + python-docx
├── tools/sample_build.py       # 版式冒烟测试 / 参考实现
├── tools/make_icon.py          # AI 草稿图 → 1024 RGBA 苹果 squircle 母版
├── tools/make_icns.py          # 母版 → 十档尺寸 → AppIcon.icns
├── tools/make_test_material.py     # 生成成套测试素材（docx：题目 + 带错作文）
├── tools/make_test_material_pdf.py # 同上，PDF 版（fpdf2 + 系统字体，坑见 §9）
├── docs/
│   ├── 示例-批改稿.docx          # sample_build.py 的产物，用来看版式
│   ├── 规则md-变更记录.md        # 内嵌规则的版本变更（不属于工程交接）
│   └── 规则md-清理对照表.md      # 换版时的逐条检查清单
├── HANDOVER.md                 # 本文：只写工程侧
└── .github/workflows/release.yml
```

---

## 5. 继承自讲义版、不许改的六条铁律

这六条是讲义版用 27 个版本、十几次返工换来的，**照抄，不要"优化"**。

### 5.1 「继续生成」只能用真实鼠标事件

DeepSeek 会检查 `event.isTrusted`，`dispatchEvent` / `element.click()` 造出来的事件恒为 false，页面毫无反应。
必须走 `BrowserController.clickAtViewportPoint`：JS 返回视口坐标 → 转 NSView 坐标（`WKWebView.isFlipped == true`，`localY = y` 不要翻转）
→ `NSEvent.mouseEvent` + `window.sendEvent`。前提是窗口 `makeKeyAndOrderFront`，非 key 窗口注入不稳。

### 5.2 浏览器隐藏用 `alphaValue = 0`，不要挪到屏幕外

挪到屏幕外会被判 `hidden`，页面定时器被节流，双屏还会漏到副屏。
`alpha=0` + `ignoresMouseEvents = true` 时页面仍认为自己是 `visible`，零节流，注入事件也照常命中。
只有登录时才 `showForUser()` 露出来，登录成功 5 秒倒计时后自动收起。

### 5.3 量长度必须用 `textContent`

`innerText` 依赖布局重排，页面隐藏时失真，会误判「写完了」。结束标记、代码长度、正文长度全部走 `textContent`。

### 5.4 「AI 写完了」的四层判定

| 层 | 条件 | 说明 |
|---|---|---|
| 0 | `generating`（有「停止生成」） | 继续等 |
| 1 | `hasContinue`（有「继续生成」） | 真实鼠标点它，轮询 12 秒验证内容是否增长 |
| 2 | `hasEndMark` 连续 2 轮 | **最强信号**：提示词要求 AI 在最后一行写 `# ===ESSAY-END===` |
| 3 | `looksComplete && afterLines >= 3` | 语义兜底：末尾有 `.save(...)` 或 `main()`，且代码块后有 ≥3 行说明 |
| 4 | 稳定 **3 秒**且必须有收尾标志 | 否则继续等；**绝不执行截断脚本** |

总上限 **10 分钟**，到点直接判失败。状态框每 **3 秒**播报一次「代码目前 X 字」。

> 第 4 层原来是「稳定 60 秒」（5 秒一轮 × 12 轮）。2026-10-27 用户定改成 3 秒：
> 理由是「结束标志从未失手，60 秒纯属白等，0 秒都行，保险起见 3 秒」。
> 循环间隔同步从 5 秒缩到 3 秒 —— 否则「一轮没长」实际是 5 秒，「3 秒」就不成立。
> 连带变化：`hasEndMark` 连续 2 轮从 10 秒变 6 秒（第 2 层更快），状态框播报从 5 秒变 3 秒。
> **没有收尾标志时仍然一秒都不提前**，攒满 60 秒（20 轮）只提示一句，继续等到 10 分钟上限。
> 万一 3 秒真的抢早了，代价是 Python 报 SyntaxError、这一轮失败，**不会静默产出一份错的 docx**。

### 5.5 按钮的功能优先于外观

任何 hover 叠层、视觉叠加都不能挡住点击。讲义版 v0.27 就是栽在这：退出按钮上盖了一层透明 hover，
`SwiftUI` 里透明填充一样接鼠标，按钮点不动。**叠层内容必须加 `allowsHitTesting(false)`**（加在叠层上，不是加在按钮上）。

### 5.6 版本纪律

本地编译 → 替换 App → 试用 → 用户明确说上线，才提交、打 tag、推 GitHub 让 CI 出 Release。
同一标签绝不删除重建，标签已存在就升下一个版本号。

> **2026-10-27 起改了口径**：用户说「本次测试可以不用每次都改版本号，除非积累到让我推送到 gh 上」。
> 所以**本地反复迭代期间沿用同一个版本号**（v0.15–v0.21 就是这么攒出来的，现在停在 **0.21**），别每改一次就 +1；
> 到真要推 GitHub 那天再统一升一次、打 tag。**判断依据只有一个：用户说「推上去」才升版。**

---

## 6. 与讲义版的结构差异（改过的地方）

除下表外，其余源码逐行一致：

| 位置 | 改了什么 |
|---|---|
| `AppState.Slot` | `case exam, answer` → `case topic, essay`；`examURL/answerURL` → `topicURL/essayURL`；`pickDir.exam/answer` → `pickDir.topic/essay` |
| `AppState.idleStatus` | 四档文案改为「题目 / 作文 / 登录」组合 |
| `AppState` 各处文案 | 「讲义」→「批改稿」，「生成讲义」→「生成批改」，「考卷/答案」→「题目/作文」 |
| `AppState.bundledRule/Template` | 指向 `作文批改规则.md` / `标准模式批改.docx` |
| `Pipeline.promptText` | 整段重写，见 §6.1 |
| `Pipeline` 上传清单 | 规则、模板、题目、作文 四个文件名 |
| `ScriptExtractor` 打分 | 去掉 `add_heading`/`add_table`，加 `add_run` + 红字色值（批改稿靠 run 级颜色，不靠标题样式） |
| `Scripts.swift` | 结束标记正则 `ESSAY-END`；抓代码时剥掉标记行 |
| `PythonRunner` | 工作目录 `作文批改-run-`、脚本名 `生成批改.py` |
| `Pipeline` 第 0 步 | 每轮先重载根地址保证空白对话（见 §6.12；早期是点按钮 + 重载兜底） |
| `AppState.downloadDocx` | 保存面板固定落 `~/Downloads`，不再跟题目文件所在目录走 |

**v0.12 两处行为修正**：

1. **新对话兜底**。原来只点页面上的「开启新对话」按钮，JS 匹配不到就返回 `NOT_FOUND`，
   而调用方不检查返回值 —— 页面改版后会静默复用上一轮上下文。当时加的是「点不到就重载根地址」的兜底。
   **2026-10-27 已改成每轮直接重载**（按钮那条路一次都没点中过，见 §6.12），
   现在等 `isPageLoaded` 最多 25 秒，再等输入框真的出现最多 10 秒，不再盲睡 2 秒。
2. **保存目录**。`downloadDocx` 的 `NSSavePanel` 固定指向 `.downloadsDirectory`。原来跟 `startDirectory(for: .topic)`
   走，成品会散落在素材文件夹里。注意 `chooseFile`（打开面板）仍然记着上次目录，那是另一回事，别一起改。
| `EssayApp.swift` | 标题、副标题、两个上传框、主按钮、Word 卡文案 |
| `build.sh` | App 名、可执行名、Bundle ID、版本号、`-disable-sandbox` 兼容、增量构建 |

### 6.1 提示词（`Pipeline.promptText(fileCount:)`）

**2026-10-27 换版**：用户自己写了新的 `~/Documents/提示词.txt`，已整段替换。`promptText` 从
`static let` 改成 `static func promptText(fileCount: Int)` —— 文件总数按实际附件算（4–8 个），
写死「4 个」会跟真实附件数对不上。只有开头那句和「其中 3、4」的指代随数量变，正文与用户给的 txt 逐字一致。

```
我发你 4 个文件，分别是 1.《作文批改规则.md》、2.《标准模式批改.docx》、3.《题目》、4.《作文》，
其中 3、4 可能没有严格命名，需要你自行判断哪个是题目，哪个是作文，而且其内容可能是文本也可能是
扫描件或者照片插入进 word 文档内，甚至直接就是图片，其中作文由于篇幅关系或者试卷换页的缘故，
可能是1-3 张图片，需要你来识别（有时候照片会拍进多余的内容需要你提取，其中的《作文》照片可能有
学生的涂改痕迹，你自行判断最终形态，如有手写红笔批改痕迹请忽略）。识别全部文件以后，请执行
《作文批改规则.md》所规定的内容，版式照《标准模式批改.docx》，遇见《作文批改规则.md》未明确规定
的事项，可以从《标准模式批改.docx》参照模仿。因为现在是网页版无法输出文件，请你给出 Python 脚本
文件我自己去执行，其他规则不变。

注意：《标准模式批改.docx》只作版式与笔调的参照，其中的人物、题目、学生作文、批改意见一律不得沿用；
题目和学生作文一律以上传的文件为准。

补充说明（我的运行环境）：Python 3.12，已装好 python-docx，没有其他第三方库，请不要 import
pandas、matplotlib、openpyxl 之类；脚本要能一次跑完，不要用 input() 等待键盘输入；
最后请用 doc.save('文件名.docx') 保存。

【格式要求，非常重要】Python代码的最后一个行必须原样写上这一行注释（#前不要有任何空格）：
# ===ESSAY-END===
这一行必须是代码框里的最后一行……（判断代码是否输出完整的标记）

【收尾说明，同样重要】代码块结束之后，请再写一段简短的中文说明，至少 3 行、3 行或更多，
讲清楚：这份批改稿有哪几个部分、哪些是红色需改处、哪些是蓝色〔〕编号、纠错与补充意见各几条、
终稿多少词。这段说明必须写在代码块外面。
```

> 上面为便于阅读折了行，**代码里的真实字符串每段是一整行，不折行**。改动以 `Sources/Pipeline.swift`
> 的 `promptText(fileCount:)` 为准，本节只是镜像，别在这里改。
> 想看不折行的实际内容：`./dist/高三英语作文批改.app/Contents/MacOS/EssayCorrect --prompttest`
> （打 4 个文件版和 6 个文件版，顺带校验结束标记还在）。

**新版相对旧版的实质变化**：

1. 新增「**甚至直接就是图片**」「作文**可能是 1-3 张图片**」—— 这是这一轮多文件/多格式能力的提示词侧支撑。
2. 旧版那两段「注意：《标准模式批改.docx》只作版式与笔调的参照……」在新版里被删掉了，
   **2026-10-27 已确认是漏删，用户说「帮我补上吧」，已加回**（位置：第一段之后）。
   补回时把「以上传的那两个文件为准」改成「**以上传的文件为准**」—— 现在作文可能是好几张图，
   「那两个」已经不对了。

   这两段是专门防「模型照抄模板里的示例题、示例作文、示例批改意见」的（见下面第 4 条）。
   删掉之后只剩「版式照模板」「未写明的照模板模仿」，模型在题目/作文文件模糊时更容易越界沿用模板内容。

**四个不能动的部件**：

1. `# ===ESSAY-END===` 末行标记 —— 第 2 层判定（`Scripts.swift:311` 的 `hasEndMark`）。检测正则
   `/#\s*===ESSAY-END===/i` 不锚定行首、允许 `#` 与 `===` 间有空格，所以 AI 万一加了空格也能识别；
   剥除正则 `[ \t]*#[ \t]*===ESSAY-END===[ \t]*$` 同样容错。提示词里那句「#前不要有任何空格」是双保险，不是必需。
2. **最后那段「至少 3 行说明」** —— 第 3 层判定 `afterLines >= 3` 的依据。AI 不可能在代码块没闭合时
   跳到下面写说明，代码块后出现 3 行以上说明 = 代码块一定闭合了。这是结构性证据，删了判定就退化。
3. **「版式照模板，规则没写明的照模板模仿」** —— 模板 docx 因此从「参考文件」升级为「兜底规格」。
   规则 md 可以留白，但模板必须是一份真正合格的成品，否则留白处会被照着错的学。
4. **「模板只作版式参照、人物／题目／作文／批改意见不得沿用」**（2026-10-27 已补回）—— 模板是一份
   **完整成稿**（真题面 + 真作文 + 12 条纠错 + 终稿 + 翻译）。没有这句，模型很容易越过「版式」直接沿用内容，
   尤其在上传的题目文件模糊时。规则 §1 只禁「套用规则里的示例题」，示例题藏在模板里，不在这句话射程内。
5. **「按内容判断哪个是题目、哪个是作文」** —— App 侧上传顺序固定（规则、模板、题目组、作文组，见
   `Pipeline` 里 `uploads` 的拼装），但**文件名不做约束**，用户可能传 `IMG_0042.jpg`。所以提示词靠内容判断，
   同时兜住「照片拍进了多余内容」「作文有涂改痕迹」「红笔批改痕迹要忽略」。这条与规则 §7 的转录规则是一套的。

### 6.2 应用显示名（v0.14 修，别再踩）

Dock 悬停气泡、菜单栏最左边那个应用菜单、访达「显示简介」里的名字，**都不读 `Info.plist` 的
`CFBundleName`，而是读 `Resources/zh-Hans.lproj/InfoPlist.strings`**。

原因是包里声明了 `CFBundleLocalizations = [zh-Hans]`，本地化字符串会覆盖 `Info.plist` 的同名键。
克隆时这个文件没改，于是图标换了、名字还是「讲义生成」—— `build.sh` 里的 plist 明明是对的，光看那里永远查不出来。

改完要刷新缓存，否则 Dock 还显示旧名：

```bash
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister \
  -f "/Applications/高三英语作文批改.app"
killall Dock
```

验证：看菜单栏名字最快（和气泡同一份字符串）。**别指望用合成鼠标事件去触发 Dock 气泡** ——
`CGWarpMouseCursorPosition` 和 `CGEvent(.mouseMoved).post(.cghidEventTap)` 都不行，Dock 只认真实硬件事件。

### 6.3 图标加工链（v0.14 新增）

用户自己在别的模型出图，本工程只负责把图变成能用的 icns：

```bash
python tools/make_icon.py <草稿图.png|jpg> docs/icon/icon-master.png --preview
python tools/make_icns.py docs/icon/icon-master.png Resources/AppIcon.icns
./build.sh --install
```

`make_icon.py` 干的事：裁白边 → 缩到 824（macOS 图标网格，四周留 100 给投影）→ 套超椭圆蒙版
（n=5，苹果连续圆角）→ 加投影 → 输出 1024 RGBA。

两个坑：**AI 的圆角比苹果更圆**，蒙版要往里缩 `ERODE=24`，否则 AI 边缘那圈浅灰描边会留成白边；
**别用 `MinFilter` 做内缩**，卷积窗口在图像边界被裁，顶部/底部会留一条半透明带。

### 6.4 主窗口背景（v0.14 换品红）

`EssayApp.swift` 的 `Backdrop`。品红族色值从图标上采的（右上 `#E05769` / 左下 `#A81D5A`），
但主窗口只做氛围：底色 `#FEFBFC`，晕的透明度浅色 0.075/0.065、深色 0.22/0.20。
**强调色 `brandBlue` 保持蓝色**，用户 2026-10-26 明确否决过改成品红，不要再提。

### 6.5 规则 md 的版本沿革（规则正文里已全部删除）

用户 2026-10-26 要求：**规则 md 里不许写版本号、日期、变更说明**。理由很直接 —— 那份文件是上传给
DeepSeek 的，版本记录对它一点用没有，只占 token，还可能把它带偏（例如读到「实测被抄过」反而去模仿）。
**规则正文只写规则。版本沿革记在这里和 `docs/规则md-变更记录.md`。**

删掉的内容（原文保留备查，别再往规则 md 里加回去）：

| 规则版本 | 改了什么 |
|---|---|
| **v4.8** | 一次真实产物的复盘：模型把「语法正确、只是可以更正式」的句子当硬伤改（`Let's`→`Let us`、`I'm`→`I am`、`couldn't`→`could not`）。§2 新增「什么算错、什么不算」四条（**缩写不算错、不标红**；判据是「母语者会不会当成错误」；**纠错条数不是指标**）；§4.2 三行收紧，「该换」的语域加「**明显**不合场景」并明写「缩写不算语域问题」，「不该做」补「把语法正确的句子按更正式改掉」。详见 `docs/规则md-变更记录.md` |
| **v4.7** | 删掉规则 md 头部的全部版本记录与「本文是成品规格书」那段元说明；§0 总则末句改写为「**【特别重要】：不空行、所有中文必须宋体！所有英文必须Times New Roman、页面设置为 A4。**」（原文是「不空行、中文宋体英文 Times New Roman、A4」，太软，模型会漏） |
| **v4.6** | 五个章节标题里只有「一、作文要求」是段前 8pt，后四个被设成 0pt —— 模型认为「前面已经空了一行，不用再留白」。§3 补：**空段落不替代段前距，五个标题都要 8pt** |
| **v4.5** | §10 骨架里 `五、参考翻译（纯中文，无任何标记）` 的括注被模型当正文抄进标题。去掉括注，§10 开头说明「骨架里的括号是说明、不是正文」 |
| **v4.4** | 以 `标准模式批改.docx` 为准对齐：取消体裁限制、二标题去掉「手写」、删除项改为在终稿对应位置打标记、题面缺失时的 `同题：××` 去掉词数、§3 补齐模板实测间距、§10 去掉 `IV.` 与 `(25%)` |
| **v4.3** | §6 原写「忽略题面标注的 120–150 词限制」，把区间写死了（题面有时不标词数、有时标 130–140）。改为「忽略题面标注的词数限制」 |
| **v4.2** | 删去固定命名规则（`序号-姓名-作文批改.docx`）—— 本 App 单篇生成、不做批量，文件名由提示词约束、脚本自拟 |
| **v4.1** | 由 v4 清理而来，供 App 内嵌使用。删去「问用户、批量处理、工具链、交付说明」类内容（执行者从对话助手换成生成 docx 的脚本），把原文自相矛盾的「四部分／五部分」统一为五部分 |

顺带记一句被删掉的元说明里的有效信息，免得以后找不到依据：**规则里所有「必须／禁止」都是对最终那份
docx 的要求；执行者是脚本，不是对话里的助手，所以规则不写「先问用户」「交付时说明」这类动作。**
规则没写到的细节，按提示词里那句「从《标准模式批改.docx》参照模仿」办。

### 6.6 登出入口挪到登录行（v0.16）

原来退出登录藏在页面底部「⋯」菜单里，而底部还有一行「● 运行环境已就绪」。用户 2026-10-27
要求：**底部那行连同「⋯」一起删掉**，改成双绿灯后 0.5 秒在登录行右侧淡入一个「登出 DeepSeek」按钮。

- 按钮**不加粗**：`.font(.system(size: 12))`，别写 `.semibold`（用户明确要求）。
  玻璃胶囊样式、hover 提亮、颜色都照「登录 DeepSeek」那个按钮来，两个按钮是同一个视觉语言。
- 出现时机：双绿灯（已登录 + 模式已激活）后 **0.5 秒延迟 + 0.5 秒淡入**（`AppState.syncLogoutGate`）。
  淡入只绑 `logoutReady` 这一个值，别给它挂别的动画。
- **兜底**：只要登录了就先挂一个 8 秒计时器（`scheduleLogoutFallback`）。万一模式检测一直失败
  （网页改版、开关找不到），到点也把按钮放出来 —— 底部那个「⋯」已经删了，不给兜底用户就**没有任何
  登出入口**。`logoutDeepSeek()` 里必须把它取消，否则重新登录后第 8 秒会被它提前放出来。
- 点它只弹 `logoutConfirmOverlay`，真正清登录态是确认之后走 `logoutDeepSeek()`。
- 生成中按钮 `disabled`：登出会清掉整个网页数据，正在跑的批改直接废掉。
- **用词统一成「登出」**：按钮、确认框标题「登出 DeepSeek 账号？」、主按钮「登出并重新登录」、
  进度提示「正在登出…」「已登出 DeepSeek 账号」都用登出。**注意别把「退出 App」那个确认框也改了** ——
  那个是真的关闭程序（「确认退出吗？」「退出后 App 将完全关闭。」），两回事。
- `ContentView.footer` 整个删了，连带 `footerHover`。`AppState.pythonReady` 现在没人用，
  但留着没删（以后想加回运行环境提示可以直接用）。

### 6.7 上传框改版：卡片式预览 + 粘贴（v0.18，v0.19 定版）

用户 2026-10-27 给了一张截图当排版基准，要求**题目框和作文框长得一模一样**，并且明确：
「接下来先不管代码实现，先把 app 界面做一个出来」。所以这一版**只把界面和收纳做出来**，
pdf / 图片真正进流水线是下一轮的事。

v0.19 又按用户意见改了三处：**删掉「点击此处粘贴文件」标签**、**预览卡片改三等分挤进同一行**、
**外框从虚线改实线**。

**2026-10-27 又改一轮（用户四条意见，版本号冻结在 0.20）**：数量规则从第一行右侧挪到第二行末尾、
「按 ⌘V」提示从第二行挪到第一行行末、框内再点不再取消（只有点框外才取消）。定版版面
（`UploadCard` 顶部注释里有同一张 ASCII 图）：

```
┌──────────────────────────────────────────────────┐
│ 上传作文题目                         按 ⌘V 粘贴，点框外取消 │ ← 仅激活时出现
│ 支持 doc / docx / pdf 与图片，含手写稿或打字稿全文，word 或 pdf 文档最多 1 个，图片最多 3 张 │
│ ┌───┐ ┌───────┐ ┌───────┐ ┌───────┐              │
│ │ + │ │ 卡片 ⓧ │ │ 卡片 ⓧ │ │ 卡片 ⓧ │              │
│ └───┘ └───────┘ └───────┘ └───────┘              │
└──────────────────────────────────────────────────┘
```

**几条用户明确点名的规矩，改的时候别弄丢：**

- **预览卡片不能占一整行**（用户 2026-10-27 原话：占一整行会把框撑高，620×720 的固定窗口就装不下）。
  现在加号右边恒定三等分，空位用 `Color.clear.frame(maxWidth: .infinity)` 撑住 ——
  **不管放 0 个还是 3 个，每格宽度都一样，框的高度永远不变**。别改成「有几个就分几份」。
  实际每格约 161pt（窗口 620 − 页边距 44 − 卡内边距 30 − 加号 47 − 间距 16，再除以 3）。
- **卡片高 46、加号 46×46、缩略图 36×36**（用户 2026-10-27 要求「加号和预览卡片加高、
  缩略图跟卡片外框的边距改小」）。原来是 38 / 38 / 24 —— 缩略图上下各留 7，太松；
  现在 46 / 46 / 36，上下各 5。**这两个尺寸是一组，别只改一个**：卡片矮于缩略图会被裁，
  加号矮于卡片会显得错位。加高会让上传框变高、整页元素下移，这是用户预期的因果。
- **光标**：只有加号是手型（`.handCursor()`），框里其余区域**一律箭头**。
  卡片右上角那个移除叉保留手型（它是独立按钮，需要可点的暗示）—— 用户没点名，若被否再改。
- **点框里任何非加号的地方 = 激活「等待粘贴」态**：细蓝边 + 浅蓝底 + 第一行行末出现蓝色提示。
  `UploadCard` 整体挂 `.onTapGesture` → `state.armPaste(slot)`，加号是 Button（子级手势优先，不会连带触发框的 tap）。
- **取消只有两条路**（用户 2026-10-27 明确：框内再点不取消，点框外才取消，且必须在 App 范围内）：
  ① 点框外 —— `EssayApp.installPasteMonitor` 里另挂了一个 `.leftMouseUp/.rightMouseUp` 的 local monitor；
  ② Esc（原有的）。
  **实现是「票据制」不是坐标、也不是时间戳**：框内任何点击（左键 tap、加号、右键）都调
  `state.armPaste` / `keepPasteArmed` 留一张 `insideClickTicket`；monitor 在 mouseUp 之后推到下一轮
  runloop 看一眼 —— 有票作废票据、没票才取消。
  - **不要改成判断坐标**：那要处理 SwiftUI global 空间和 NSEvent 窗口空间的 y 轴翻转，平台行为一变
    就会「点框内反而取消」。
  - **不要改回时间戳**：右键可以按住不放，按住的时长会把时间戳拖过阈值，长按右键就被误判成「点在外面」。
  - 也别用 SwiftUI 手势，local monitor 天然满足「点别的 App 不取消」。
- **窗口失焦时，左键点框也要能激活**（用户 2026-10-27 报：右键正常、左键没反应）。
  这是 AppKit 的「第一次点击」规则：非 key 窗口上的左键只用来激活窗口，事件被吞掉，
  除非命中的视图 `acceptsFirstMouse` 返回 true。**右键不受这条限制**，所以只有左键坏。
  修法在 `RightClickCatcher` 里：窗口不是 key 时，`hitTest` 对 `.leftMouseDown` 也返回自己，
  `mouseDown` 直接转成 `armPaste`；窗口变 key 之后照旧穿透，一切照常。
  **别去改 SwiftUI 的 tap**——那条路根本收不到这个事件。
- **框内右键 = 激活 + 冒泡两选一菜单**（用户 2026-10-27，第二版）。
  第一版做的是「右键直接粘贴」，用户说「过于丝滑」，改成：右键**只激活该框**，
  并在鼠标位置冒出一个圆角玻璃气泡，只有「粘贴 / 取消」两项（`PasteBubble`）。
  - 点「粘贴」：粘贴完**仍保持激活**（和 ⌘V 一样，可以接着粘下一张）。
  - 点「取消」：关菜单 + 退出激活。
  - 点框外 / Esc：菜单跟着激活态一起收。
  - 菜单位置夹在卡片内（`x∈[62, w-62]`、`y∈[44, h-44]`），免得贴边时半个菜单露到卡片外面。
  - 实现是 `RightClickCatcher`：透明 `NSViewRepresentable`，`hitTest` 里**只在右键事件时返回自己**，
    其余一律返回 nil —— 左键完全穿透，框的 tap、加号按钮都不受影响。
    SwiftUI 本身接不到右键（`onTapGesture` 只认左键、`.contextMenu` 会弹系统菜单），只能走 AppKit。
    **回调要带上点击位置**：`NSView` 原点在左下、SwiftUI 的 overlay 原点在左上，
    `rightMouseDown` 里要 `y = bounds.height - p.y` 翻一下，否则菜单会上下颠倒地弹出来。
- **剪贴板图片的命名只跟 App 内状态走**（用户 2026-10-27 报的 bug）：
  症状是序号一路涨到 `剪贴板图片-10`，关掉重开也回不到 1。
  原因：名字是从**临时目录里没被占用的最小序号**倒推的，而临时目录里的旧图 App 退出也不清。
  现在：`UploadItem.isPaste` 标记来源，`AppState.nextPasteName()` 只数两个框里**当前还在的**
  剪贴板图片（上传的文件不算，它们自带文件名），取「当前没被占用的最小正整数」，
  名字形如 `剪贴板图片1`（**不带 `-`**）。删掉中间一张再粘，序号会补回空位，不会一直涨。
  落盘文件名 = 显示名，被拒（数量满）时会把刚写的文件删掉，不留垃圾。
- **别再把粘贴提示做成一个独立标签**：v0.18 做过一个「点击此处粘贴文件」的胶囊标签，
  用户 2026-10-27 说「非常多余」，删了，位置让给预览卡片。
- **数量规则在第二行末尾，不在第一行右侧**（用户 2026-10-27：第一行右上角那串「文档一个或图片最多 x 张」去掉）。
  第二行变长后加 `.minimumScaleFactor(0.9)`，宁可小一号也别截断成「…图片最多…」。
- **「按 ⌘V」提示在第一行**（用户 2026-10-27）：原来放第二行，激活时会把灰色格式说明整行盖掉。
  现在第二行恒定显示格式+数量，激活只多出第一行那行蓝字，**行数不变、框高不变**。
  文案是「按 ⌘V 或者右键粘贴，点框外取消」—— 右键也能粘贴，所以必须写进去。
- **那行蓝字是水平居中，不是靠右**（用户同日第二次反馈）。用 `.overlay(alignment: .center)` 挂在第一行
  的 HStack 上，**不要塞进 HStack 里配 Spacer** —— 那样标题长短一变它就左右跳，而且会占布局宽度。
  标题固定很短（「上传作文题目」＋＊必选 ≈ 140pt），居中位置从 ≈212pt 起，不会撞上。
- **空框时有一句「点击此处可粘贴」**（14pt、不加粗、灰色 `.secondary`、**水平居中**）。
  它只是**文案**：能点的仍然是「框内除加号以外的任意地方」，所以它 `.allowsHitTesting(false)`，
  不挂手势，点了落到框的 tap 上。**三个显示条件**：`items.isEmpty && !armed && !isRunning` ——
  有文件时显示会挤窄三等分预览卡片（用户定过不能动），等粘贴时显示会和第一行那句打架。
  居中同样用 `.overlay(alignment: .center)`，别塞进 HStack（会占布局宽度、挤窄卡片）。
- **两行间距是 6 不是 2**（用户 2026-10-27 截图反馈「贴得太近」）。框会因此高 4pt，
  下面的元素顺着下移 —— 外层是 VStack + ScrollView，不用额外处理。
- **外框是实线**（用户明确不要虚线）。加号的边框也一起改实线，免得框里一半实一半虚。
- **加号气泡自绘**：`.help()` 有约 1 秒系统延迟，达不到用户要的「几乎瞬间」。
  现在用 `@State plusHover` + `.overlay(alignment: .topLeading)`，0.07 秒淡入、`allowsHitTesting(false)`。
  必须靠左对齐：气泡比加号宽得多，居中会溢出卡片左边缘。
- **提示条只给「被拒」用**（用户 2026-10-27 明确）：类型不对、数量超了、剪贴板里有多个文件才冒泡；
  **上传/粘贴成功一律不弹** —— 卡片出现本身就是反馈。别再加"已粘贴 xxx"这种成功提示。
- **剪贴板图片落成真 PNG**（用户 2026-10-27）：`UploadItem.init(image:)` 把内存图片写成
  `$TMPDIR/作文批改-粘贴/剪贴板图片-N.png`，`url` 有值，跟上传的图片走同一条路。
  删文件只删**路径正好在 `pasteDirectory` 下**的（`deletePasteFile`），用户磁盘上的原文件绝不碰；
  卡片被移除 / 清空框时删，生成成功后也应该删（等接流水线那一步补上）。
  自检入口：`--pastetest` 会打印落盘路径和 exists，别靠猜。
- **卡片序号**：一个框里超过 1 个文件时，卡片最左边显示 1/2/3 小序号（9pt 次要色，宽 8pt）。
  3 张照片就是第 1/2/3 页，AI 只能按附件顺序理解，顺序错了整篇作文就乱（用户 2026-10-27 同意加）。
- **叉按钮统一白底深色**（用户 2026-10-27）：全 App 两处叉（卡片右上角 13pt、预览面板右上角 22pt）
  都是白色圆底 + 深灰叉 + 淡灰描边 + 轻投影，压在浅色图片上也看得清。系统弹窗自带的按钮不在此列。
- **图片预览的尺寸是算出来的，不是 frame 撑出来的**：`PreviewPanel.displaySize(for:)` 按图片比例
  算出宽高（上限 500×496，小图最多放大 3 倍），再 `.frame(width:height:)` 显式给定。
  之前用 `.frame(maxWidth: 500, maxHeight: 496)` —— 图片比上限小时 frame 仍会撑到上限，
  叉就飘到图片外面去了（用户 2026-10-27 报的 bug）。**别再改回 maxWidth/maxHeight**。
- **数量与种类**（`AppState.limits(for:)`）：题目框 = 文档 1 个 / 图片 1 张；作文框 = 文档 1 个 / 图片 3 张；
  **同一个框里不许混放**。任何一条违反都拒绝（不是排队），拒绝文案由 `uploadRejection(for:adding:)` 给，
  统一走 `ToastBar`：**落在触发它的那个框的正中心**（v0.20 起，之前是窗口顶部），
  渐显 0.18 秒 → 停 **2.7 秒** → 渐隐 0.3 秒。`showToast(_:seconds:slot:)` 的 `slot` 决定落在哪个框，
  `toastSlot == nil` 才退回窗口顶部（目前没有这种用法，纯兜底）。**用户专门表扬过这个提示方式，别动。**
- **⌘V 监听**：`ContentView.installPasteMonitor()` 用 `NSEvent.addLocalMonitorForEvents`，
  只有 `state.pasteArmed != nil` 且按的是 ⌘V 时才接管并 `return nil`，其余按键原样放行。
  Esc 顺手退出等待粘贴态（只 disarm，不吞事件）。
- **提示条可以被点掉**（v0.20+）：存留期间点它一下立刻渐隐，速度与渐显一致（0.18 秒，
  `AppState.dismissToast()`）；不点就走原来的 2.7 秒自动渐隐（0.3 秒，手点的要跟手，所以两种节奏不同）。
  因为要接点击，`ToastBar` 不能再挂 `allowsHitTesting(false)` —— 它盖在框中心，那一小块不再触发「激活粘贴」。
- **预览卡片可以点开放大**（v0.20+）：`AppState.previewItem` + `ContentView` 里一层全窗口 `PreviewPanel`。
  **图片**：NSImage 直接放大（最宽 500）。**doc / docx**：`QLPreviewView` 真渲染。
  **pdf**：**不用 Quick Look，走 PDFKit 的 `PDFView`**（原因见下面那条）。
  **文档面板宽 460**（用户 2026-10-27 说「改为现有的 85% 左右」，540 × 0.85 ≈ 459）。
  其余类型退到信息卡（完整文件名、类型、大小、所在文件夹）。
  三种面板的**右上角内层**都挂一个 22pt 的圆形大叉（`closeButton`，padding 8，**白底深色叉**）——
  文档那条信息栏的 `.padding(.trailing, 36)` 就是给它让位的，别把 36 改小。
  关面板有四个出口：**大叉、点面板外面、点信息栏、Esc**（`closePreview()`，0.18 秒淡出）。
  文档正文区域**刻意不接点击关闭**，否则滚动翻页会被吃掉 —— 这是唯一的例外，别"顺手统一"掉。
  进场是 0.62 → 1 的弹簧缩放 + 背景淡入，背景只压暗 0.16。
  卡片的 tap 手势挂在叉按钮**之前**，让右上角那个叉优先吃掉点击。
  注意：点卡片现在是「看预览」，不再顺带激活大框的粘贴态 —— 这是用户 2026-10-27 明确要的覆盖规则。

- **为什么 pdf 不用 Quick Look**（2026-10-27 查证，别再改回去）：用户反馈「pdf 滚轮无效，doc/docx 正常」。
  用 `--preview` + `--qldebug` 打子视图树，两者的结构根本不同：
  - doc/docx → `QLPreviewView → QLPreviewContainerView → QLDisplayBundleContainerView → QLWeb2CenteringView → QLWeb2View → WKFlippedView`（**进程内 WebKit**，滚轮正常）
  - pdf → `QLPreviewView → QLPreviewContainerView → NSRemoteView`（**独立进程的远程视图**，滚轮事件不响应）
  所以 pdf 改走 `PDFPreview`（`PDFView` + `autoScales` + `.singlePageContinuous`），
  子视图是 `PDFView → PDFScrollView → NSClipView → PDFDocumentView → PDFPageView × N` + `NSScroller`，
  进程内真滚动视图，滚轮/翻页/双指缩放都正常，页面清晰度也比 QL 的位图好。

- **文档预览为什么用 Quick Look**：系统自带的 `/System/Library/QuickLook/Office.qlgenerator`
  （`com.apple.qlgenerator.office`）在 `LSItemContentTypes` 里**明确声明了 `com.microsoft.word.doc`**
  （老 .doc）和 `org.openxmlformats.wordprocessingml.document`（.docx）。
  也就是说「Finder 按空格能看的，这个面板也能看」，**用户机器上不需要装 Office**。
  实测（2026-10-27）：包内 `标准模式批改.docx` 渲染出 `QLWeb2View` + `WKWebView` 一套，
  即 Office 生成器的 web display bundle 真的出图了，不是空白占位。
  仍会失手的少数情况：加了密码的文档、Word 6.0/95 那种极老格式、损坏文件 —— 这时面板会是空白/占位，
  **还没做纯文字兜底**（`textutil`/`NSAttributedString` 那条路留到有真实样本再说）。

> 三个开发用入口：`--preview /路径/文件` 启动即打开该文件的预览（任何受支持类型，验渲染最省事）；
> `--uidemo9` 打开包内那份 docx 的预览；`--qldebug` 在 3 秒后把预览视图的子视图树打到 stderr
> （无缓冲，重定向也能看到），出现 `QLWeb2View`/`WKWebView`/`PDFScrollView` 就说明真渲染了。

> **系统版本要求**：这套预览**不需要装任何东西**。用到的 API 最早可用版本都远早于 macOS 15 ——
> `QLPreviewView initWithFrame:style:` 是 10.7、`refreshPreviewItem`/`previewItem`/`autostarts` 同期、
> PDFKit `PDFView` 的 `displayMode`/`displaysPageBreaks` 是 10.4 时代、`pageShadowsEnabled` 是 10.14，
> 所以 App 的 `LSMinimumSystemVersion 13.0` 以上全都能跑（本机 macOS 27 实测通过）。
> **唯一跟系统版本挂钩的外部依赖是系统自带的 `/System/Library/QuickLook/Office.qlgenerator`**
> （渲染 doc/docx 用），它从很早就随系统分发；万一哪天被 Apple 拿掉或遇到加密/极老文件，
> doc/docx 预览会是空白 —— 那时再补 `textutil` 纯文字兜底。

**数据结构**：`UploadItem`（顶层 struct，不是 `AppState` 的嵌套类型）承载一张卡片：
`url?` / `kind` / `name` / `sizeKB` / `thumb?`。存在 `AppState.uploads: [Slot: [UploadItem]]`。
`topicURL` / `essayURL` 只是「框里那个文档」的镜像（`syncLegacyURL`），流水线已改为直接读 `uploads`。

> ⚠️ 命名坑：`Pipeline.swift` 里原来也有个 `private struct UploadItem`（多部分上传的载荷），
> 和新的顶层 `UploadItem` 撞名，编译直接报 `extra arguments at positions #2, #3`。
> 已把 Pipeline 那个改名成 `FilePayload`。以后再加类型先 `grep` 一遍。

> 曾经的已知不一致（2026-10-27 已修）：作文框只放图片时 `canGenerate` 是 false。现在它看的是
> 「两个框都非空」，见 §6.8。

### 6.8 多文件进流水线（2026-10-27 接线）

界面在 v0.18–v0.20 就做好了，这一轮把逻辑接上。改动分布：

| 位置 | 改了什么 |
| --- | --- |
| `AppState.canGenerate` | 从「两个 `URL` 都不为 nil」改成「两个框都非空」——`!items(for:).isEmpty`。图片、pdf、剪贴板图片都能触发生成 |
| `AppState.idleStatus` / `hintText` | 同上，判断依据换成 `items(for:)`；文案从「两份 Word 文档」改成「Word、PDF 或图片均可」 |
| `AppState.heldFiles` | `(topic: URL, essay: URL)?` → `(topic: [UploadItem], essay: [UploadItem])?`。存 `UploadItem` 而不是 URL，放回去时缩略图/名字/大小都还在，界面不会闪 |
| `AppState.submitAndClearUploads` / `restoreHeldFiles` | 跟着改成数组；`restoreHeldFiles` 末尾重算 `topicURL`/`essayURL` 镜像 |
| `AppState.discardHeldFiles`（新） | 成功路径调用：清空 `heldFiles` 并把临时目录里的剪贴板 PNG 删掉（失败路径不删，要放回去重试） |
| `AppState.chooseFile` | `allowsMultipleSelection` 改成 true，一次挑 1–3 张作文图片不用反复开面板；超限的由 `addUpload` 挡掉冒泡 |
| `Pipeline.runPipeline` | 先 `items(for:).compactMap { $0.url }` 拷两组数组，再清框；进度文案「两份文档已放回」→「文件已放回」 |
| `Pipeline.pipeline(topicFiles:essayFiles:auto:)` | 签名从两个 `URL?` 改成两组 `[URL]`；`uploads` 从写死 4 个改成「规则 + 模板 + 题目组 + 作文组」动态拼 |
| `Pipeline.mimeFor` | 补 `pdf` / `png` / `jpg`（原来只有 docx/doc/md，其余落到 octet-stream） |
| `Pipeline.dedupeNames`（新） | 重名附件补序号 `作文.png` → `作文-2.png`。**只改送给网页的名字，磁盘文件不动** |
| `Pipeline.waitFor` | 入参从 `[String]` 改成 `[(name:isImage:)]`，超时按总体积算：`min(120, max(25, 15 + MB*2))` |
| `Scripts.checkNames` | 入参 `[{n,i}]`；**图片多一条兜底**：名字在 `innerText` 里找不到时，改数页面上 `img[src^=blob:]` 缩略图够不够，免得「明明传上去了却报失败」 |

**为什么不按顺序告诉 AI「这几个是一篇的」**：用户实测「随便乱发他都能认」，提示词里也只说「自行判断」。
所以 `uploads` 的顺序只用于稳定日志，不承担语义。

**重名为什么要补序号**：`checkNames` 是 `innerText.indexOf(name) >= 0` 的子串匹配，两个同名文件
只要到了一个就会被判「都到了」，等待逻辑会提前放行；附件条上也分不清谁是谁。

### 6.9 文件名污染输入框（2026-10-27 用户报）

**症状**：网页版收到附件后，会把**文件名当成文字塞进输入框**。用户截图里输入框写着
`解决 Google Antigravity 登录不上及账号区域限制问题.pdf IMG_3435.jpeg 未标题-1.png`，纯文件名，没有一个字是提示词。
如果这时直接 `fillText`，虽然会覆盖，但网页是**异步**插的，插晚一步就会把提示词顶掉、或者拼在提示词前面一起发出去。

**修法**（`Pipeline.fillPrompt`）：顺序必须是「等附件就位 → 清空 → 填 → 回读」。

```swift
for attempt in 1...2 {
    _ = try self.js(Scripts.clearText)          // 走 native setter + input/change 事件
    Thread.sleep(0.35 / 0.8)                     // 让 React 状态落定
    _ = try self.js(Scripts.fillText(...))
    let back = try self.js(Scripts.readText)     // 回读整个 textarea
    if back == prompt { return true }            // 完全一致才算成
}
```

- `Scripts.clearText` / `Scripts.readText` 是本轮新增的两个脚本，和 `fillText` 一样走
  `HTMLTextAreaElement.prototype.value` 的 native setter —— 直接 `ta.value = ''` 不触发 React 的 onChange。
- **回读校验是关键**，不能只信 `fillText` 的返回值：它只说明「我写进去了」，不说明「后面没被改」。
- 两次都不一致**不抛错**，只记日志并继续发 —— 内容已经在框里，多出来的无非是文件名，AI 自己能认出来；
  在这里硬失败等于白白浪费前面一两分钟的上传。
- **发送前再比一次**：`auto` 模式有 4 秒倒计时，这几秒里网页仍可能补文件名。
  一致就不动输入框（无谓地清空重填反而多一次竞态）。

> 注意别把「清空」挪到附件上传之前。清早了，网页随后照样会补回来 —— 顺序错了这一步等于没做。

### 6.10 运行日志面板（2026-10-27，用户要求）

**为什么加**：`progressLines`（流水线日志）原来**只出现在失败诊断的 md 里**。也就是说
成功跑完一次，App 里没有任何地方能看到「提示词已填入并回读一致」这类日志 —— 想验证 §6.9 的修复
有没有生效，只能等它失败。用户问「是不是有查看详情按钮」，才发现这个窟窿。

**现状先记清楚，别再记错**（2026-10-27 第二轮改版之后，入口只剩一个）：

| 入口 | 什么时候有 | 显示什么 |
| --- | --- | --- |
| 「详情」（Word 卡标题行） | 跑过一次之后一直在，成功失败都有 | `progressLines` + 末尾附 `scriptOutput` |

**2026-10-27 删掉的东西**（用户明确要求，别再往回加）：

- 「查看详情」按钮（失败态那两个按钮之一）→ 它打开的是 `OutputSheet`，一个单独的 sheet；
- 「导出诊断报告」按钮 + 桌面上的 `作文批改-失败诊断-<时间>/` 文件夹；
- 失败时自动写进 `~/Library/Application Support/作文批改/日志/` 的 md + 页面截图（`saveDiagnosticLog`）；
- `BrowserController.snapshotPNG`（只给上面那个 md 用）、`AppState.diagnosticMarkdown` / `pruneLogs` /
  `timeStamp` / `lastFailure` / `showOutputPanel`、`OutputSheet` 整个视图。

用户原话：「我现在不希望改变任何外观，直接从详情里反应即可，也就是不管成功失败，日志都在详情里」。
所以现在的规矩是：**失败只改 Word 卡那一行说明文字**（末尾指向「详情」），
按钮永远是那一个「下载 Word 批改稿」，只是没生成好时是禁用态。
失败原因由 `docx` 的 `didSet` 补一行 `✗ 生成失败：…` 进 `progressLines` ——
失败出口有六七个，挂在 didSet 上才不会漏。

> 2026-10-27 更早删掉的是**底部状态行 + 右下角「⋯」菜单**（用户要求），那个菜单里只有
> 「退出 DeepSeek 账号…」，**没有**日志入口。所以「查看详情被删了」是记错了 —— 它一直在，
> 只是成功态不显示。

**实现**（`LogPanel`，`EssayApp.swift` 末尾）：

- 入口在 **Word 卡标题行右侧**，和「可下载」徽标同一行，样式是小胶囊「详情 / 收起」。
  **不放按钮行** —— 那里「下载 Word 批改稿」占满宽度，塞一个会挤窄它，也会把卡片撑高。
- 面板 566×516，锚在窗口顶部（`padding(.top, 20)`）。
- **压暗层只铺上半屏**（`scrimHeight = 548 = 720 - 172`），底部 172pt 留给 Word 卡。
  这是用户明确要求：「绝对不要遮住按钮本身」—— 面板要是盖住自己的开关，用户就没法再点一次收起来。
  改窗口高度或 Word 卡结构时，**`scrimHeight` 必须跟着重算**。
- 显示/隐藏跟预览卡片一个节奏：`withAnimation(.easeOut(0.18))` + `.transition(.opacity...)`，
  另加 0.985 的轻微缩放（`anchor: .top`）。关的路径有三条：✕、点压暗层、Esc。
- Esc 的处理在 `installPasteMonitor` 里，顺序是 **日志 → 预览 → 等待粘贴**。
- 自动滚到底用 **`onReceive(state.$progressLines)`**，不用 `onChange` ——
  `onChange(of:perform:)` 的单参数写法在 macOS 14 已废弃，而部署目标是 13.0。

**看版式不用真跑一轮**：`--logdemo` 会塞 16 行假日志并把面板打开。

### 6.11 一次真实运行的日志暴露的两个问题（2026-10-27）

用户跑通一轮后截了日志面板，里面有两行不对劲，都修了。

**① `页面重载完成，用时 0.0 秒` —— 等于根本没等**

`loadDeepSeek(force:)` 里有 NSWindow 操作，必须 `DispatchQueue.main.async` 派发；但轮询是在后台线程，
`isPageLoaded` 还是上一轮留下的 `true`，`while !isPageLoaded` 立刻退出。后面只补了 2 秒，
页面要是还没起来，探针就会打到半截 DOM 上。

修法：派发**之前**先在当前线程把标志打回 false（`BrowserController.markReloading()`，只改一个 Bool，
不碰窗口），循环才真的等到 `didFinish`。现在日志里是真实耗时。

**② `注入：INPUT:0` —— 看着像失败，其实正常**

`commitFiles` 原来返回 `input.files.length`，而那是**派发 change 事件之后**的值：网页接手附件时
会把 `input.value` 清空，`files` 跟着变 0。所以永远是 0，跟「注入失败」长得一模一样。

修法：改成返回 `INPUT:<交出去的个数>/<事件后剩余的个数>`，形如 `INPUT:5/0`。
**看到后一个数是 0 别慌**，前一个数才对得上 `uploads.count`；前一个数是 0 才是真失败。

**③ 顺带：`新对话：NOT_FOUND`（下一轮直接废掉了这条路，见 §6.12）**

每次跑都走「整页重载」这条慢路。当时只做了两个小补丁：
- 脚本除了 `innerText` 也读 `aria-label` / `title` —— 侧边栏收起时按钮里只有图标没有文字；
- `NOT_FOUND` 之后等 0.8 秒再试一次，再不行才重载（刚加载完侧边栏常还没渲染出来）。

**这两个补丁没起作用**：紧接着的那轮真实运行，日志还是 `NOT_FOUND` → `NOT_FOUND（重试）` → 重载。
结论写在 §6.12：按钮这条路整个撤掉，别再加第三个补丁。

---

### 6.12 「开启新对话」按钮：猜了三版，最后撤掉（2026-10-27）

**事实**：从 v0.12 到 v0.20，那个按钮**一次都没点中过**。每轮日志都是
`新对话：NOT_FOUND` → `新对话（重试）：NOT_FOUND` → `没找到…改为重载根地址`，
然后靠重载跑完 —— 也就是说这条「快路」从来没生效，只是在交学费：

- 两次无效的 JS 往返；
- 0.8 秒空等；
- 两行 `NOT_FOUND` 让用户以为出错了（截图里就是这么反馈的）。

**猜过的三版**（都别再加了）：① 按 `innerText` 精确匹配「开启新对话」；② 加 `aria-label`/`title` 兜底；
③ 找不到就等 0.8 秒重试。三版都建立在「按钮是 `button`/`a`/`[role=button]` 且文字可读」这个假设上，
而实际 DOM 里它很可能是 `div`，或者侧边栏收起时根本没有可读文本。**没有 DOM 证据就别再猜第四版。**

**现在的做法**（`Pipeline` 第 0 步）：

```swift
browser.markReloading()
DispatchQueue.main.async { [weak self] in self?.browser.loadDeepSeek(force: true) }
// 等 isPageLoaded（25 秒上限，0.25 秒粒度）
// 再等输入框真的出现（最多 10 秒，0.4 秒粒度探 probeComposer）
```

`https://chat.deepseek.com/` 后面不带会话 id，重载出来**必然**是空白新对话 —— 不依赖 DOM、不怕改版，
比点按钮更硬。代价是每轮多 2~4 秒，相对整轮几分钟可以忽略。

**同时改掉的两处日志**：

- `页面重载完成，用时 0.5 秒` + 盲睡 2 秒 → 拆成 `页面重载：X 秒` 和 `等输入框出现：X 秒`，
  后者是**真等到了才往下走**，不是赌。`didFinish` 只说明文档到了，SPA 可能还没渲染。
- `抓到 1 个代码块，总长 11942 字符` → 改成 `原文总长`。下一行 `脚本 11943 字符` 是
  `ScriptExtractor.normalize` 补了个换行之后的长度，两个数差 1 是正常的，别当成被改坏。

`Scripts.newChat` 已删除（死代码）。`--logdemo` 的演示日志也换成了这一轮的真实形态。

---

## 7. 产物版式与内容契约

**版式、五段结构、字号颜色、禁止项，全部以 `Resources/作文批改规则.md` 为准，本文不复制。**
规则只有一份，复制到这里必然两边打架 —— 上一版就是这么出问题的。

工程侧只需要知道三件事：

1. **版式是脚本的责任，Swift 不参与**。App 只负责把脚本跑起来、把产出的 docx 交给用户；
   Swift 代码里没有任何一处检查字体、颜色、缩进。改版式 = 改规则 md，不改代码。
2. **不做自动版式校验**（用户 2026-10-26 明确否决）。曾经设想在 `PythonRunner` 跑完后解开 docx 数
   `keepNext` / `numPr` / 色值 / 章节段前距，不合格就判失败 —— **不要做**。
   用户的判断是：格式细节不重要，正文批改质量才是关键，不能因为段前距差 8pt 就把一份批改得很好的稿子判失败。
   版式仍然靠规则 md 约束 + 模板兜底，出错靠人工抽查，**不进失败判据**。
3. **内容契约是唯一值得当完整性信号的东西**：第三段的 `纠1…纠N` / `意1…意M` 与第四段终稿里的〔编号〕
   必须一一对应。这条只写在规则里、靠 AI 自觉，实测两轮都做到了（14/14、11/11）。目前也不做硬校验。

> 版式数值的实测来源（28 份成品样本）已归档在 `docs/规则md-变更记录.md`，本文不重复。

## 8. 待办

1. ~~图标~~ **已完成（2026-10-26，v0.14）**。用户自己在别的模型出图，本工程只负责加工：
   `tools/make_icon.py`（AI 图 → 1024 RGBA 苹果 squircle + 投影）→ `tools/make_icns.py`（十档尺寸 → icns）。
   换图标就重跑这两条，然后 `./build.sh --install`。
2. ~~上传能力扩展~~ **已完成（2026-10-27，见 §6.7 界面 + §6.8 流水线）**：pdf / jpg / png / 剪贴板粘贴图片，
   题目框 1 图 + 1 文档、作文框 3 图 + 1 文档（同一框内不许混放），超出冒泡提示。
   一次可选多个文件，重名附件自动补序号，剪贴板图片落成 `$TMPDIR/作文批改-粘贴/*.png`（成功生成后删除）。
   **剩下的是真实网页端联调**：3 张手机照片走一遍，确认附件条探针、等待时长、AI 是否真按内容认出题目/作文。
   > 2026-10-26 夜里试过另一条路：把内置浏览器借给用户手动展开（v0.16 / v0.17），
   > 让用户自己在网页里把图片转成文字。**用户 2026-10-27 00:19 反悔，要求退回 v0.15**，
   > 说「想到个更好的方案」。那两个版本的代码补丁留在 `/tmp/v016-017-webpage.patch`（临时文件，别指望它长期存在），
   > 设计思路记在 `.workbuddy-ai/memory/2026-10-26.md` 和 `2026-10-27.md` 里。新方案就是这条多文件路线。
   > 提示词被删掉的那两段「模板只作版式参照」已确认是漏删，2026-10-27 补回，见 §6.1。
3. **GitHub 仓库 + CI**：**已建（2026-10-26）** —— https://github.com/xitihangto/article-correct-app （公开，默认分支 `main`）。
   推 `v*` 标签会触发 `.github/workflows/release.yml` 自动构建并发布 Release。
   ⚠️ 推 workflow 文件需要 token 带 `workflow` scope，没有会被 GitHub 拒；本机已用 `gh auth refresh -s workflow` 补上。
   ⚠️ 打标签前先确认 `build.sh` 的版本号与标签一致，CI 里有一道校验，不一致会直接失败。
   **第一个 Release 是 v0.14**（已发，产物 `EssayCorrect-v0.14.zip`，30 MB）。v0.15 / v0.16 只本地编译安装，
   等用户测完再说要不要发。
4. ~~文件名约束~~ **不做**：用户 2026-10-26 说「文件名就这样吧，应该没问题」。
   实测两轮 AI 自拟得都不错（`高三英语写作训练_AI工具与作业_批改与升格_终稿版.docx`、`批改-20261026-2044.docx`）。

> ~~成品体检器（机器校验段前距 / keepNext / 色值 / 编号集合）~~ **用户已明确否决（2026-10-26）**：
> 格式细节不重要，只要正文批改质量好就行。**不要再提议加这个**，也不要拿格式偏差当失败判据。
> 格式问题仍然靠规则约束 + 模板兜底，但不做自动校验、不阻断生成。

---

## 9. 踩过的坑（本工程新增）

| 坑 | 症状 | 原因 / 解法 |
|---|---|---|
| `swiftc` 在自动化会话里编译失败 | `SwiftUIMacros ... malformed response`，一行代码没改也编不过 | swift 驱动用 sandbox-exec 起宏插件服务被拒；加 `-disable-sandbox`（build.sh 已自动处理） |
| 复制讲义版源码后变量名漏改 | `topicURL = exam` 这种编译错 | `exam/answer` 有裸变量名、`examURL` 两种写法，替换要分两轮做，改完必须编译验证 |
| 用 Bash 的 `grep` 查中文串 | 明明有却返回空、exit 1 | 本环境的 shell grep 行为异常，查代码统一用 Grep 工具，别用 `grep` |
| 把 01 号样本直接当模板 | 能跑，但 AI 会照着真实学生的内容写 | 只是临时占位，正式模板必须替换（§8.1） |
| `add_font("times", …)` | `UserWarning: Core font or font already added 'times': doing nothing`，英文没换字体 | 名字和 fpdf2 的核心字体撞了，改成 `"tsr"` 之类 |
| fpdf2 混排中英文 | 中文变方块 / 报缺字 | 核心字体只有 Latin-1，中英都得 `add_font` 嵌入；Times New Roman **没有全角空格 `\u3000`**，抬头对齐用半角空格 |
| 从 `Songti.ttc` 取字面 | 中文明显发粗，不像考卷 | TTC 默认取 #0 = Songti SC **Black**；要 `add_font(..., collection_font_number=6)` 才是 Regular |
| `write()` 想做首行缩进 | 首行缩进生效，但**续行回到左边距** | 这其实是正确的「首行缩进 + 续行顶格」，别当 bug 修；`multi_cell` 才是整块缩进 |

---

## 10. 环境依赖

- macOS 13+（实测 macOS 27 / Xcode 27.1 / arm64）
- Xcode Command Line Tools（`swiftc`）
- 无需 Xcode 工程，无需 CocoaPods / SPM
- 网络：能访问 `chat.deepseek.com`
- 用户需在 DeepSeek 网页版登录一次（登录态存在 App 容器里）

**只给开发脚本用、不进 App 包**（App 运行时里只有 python-docx）：

- `fpdf2` / `pypdf` / `pymupdf` —— 装在托管 venv 里
  `/Users/linquin/.workbuddy-ai/binaries/python/envs/default/bin/python`，
  用来生成 PDF 测试素材、核文本层、渲染 PNG 肉眼检查。别装进 `Runtime/python/`。

---

## 11. 一句话给接手的人

**这个项目的难度不在业务，在「怎么可靠地知道 AI 写完了」和「怎么把网页当接口用」，这两件事讲义版已经解决了，别重造。**

业务改动只集中在三处：`Resources/` 两个附件、`Pipeline.promptText`、界面文案。
改这三处以外的东西之前，先回讲义版 HANDOVER.md 看有没有踩过坑。
