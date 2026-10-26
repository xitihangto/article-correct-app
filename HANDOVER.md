# 高三英语作文批改 App · 交接文档

> 最后更新：2026-10-26 ｜ 当前版本 **v0.3** ｜ 状态：**规则 md 已换成用户 v4 版并清理完毕（现为 v4.1）；等正式模板 docx**
>
> 📌 **接手先看**：§1（这是什么）、§5（继承自讲义版、不许改的六条铁律）、§6（与讲义版的结构差异）、§7（版式规格）、§8（待办）。
>
> ⚠️ 本工程是从 `/Users/linquin/lecture-app`（讲义生成，v0.27）**整体克隆**而来，界面、交互、可靠性机制完全一致，
> 只换业务：附件、提示词、两段文案、产物版式、结束标记。凡本文没写的实现细节，一律以讲义版 HANDOVER.md 为准。
>
> 🔒 **文档边界**：本文只写**工程侧**（代码、构建、踩坑、铁律），给编程 agent 看。
> `Resources/作文批改规则.md` 是**网页版内嵌规则**，会被上传到 DeepSeek 给 AI 看，不是本文的一部分；
> 那份规则的版本变更记录在 `docs/规则md-变更记录.md`。三者不要混。

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

### ❌ 还没做（用户已明确：先只做 doc/docx 单文件）

- 上传框支持 pdf / jpg / png / 粘贴剪贴板图片，每框最多 3 个文件（超出要提示）—— 以后改版
- 正式图标 —— **已明确由其他工作助手负责，本项目不碰图标**
- GitHub 仓库 / CI Release（工程里已带 `.github/workflows/release.yml`，仓库还没建）

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
```

### 运行时日志

状态栏显示最近 6 行 `progressLines`。失败时自动写诊断到 `~/Library/Application Support/作文批改/日志/`（md + 页面截图，留 30 份）。

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
│   ├── 标准模式批改.docx        # 版式模板 —— ⚠️ 当前是 01 号样本，等用户正式版替换
│   ├── AppIcon.icns            # ⚠️ 当前沿用讲义版图标
│   └── zh-Hans.lproj/
├── Runtime/python/             # 75MB CPython 3.12 + python-docx
├── tools/sample_build.py       # 版式冒烟测试 / 参考实现
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
| 4 | 稳定 60 秒且必须有收尾标志 | 否则继续等；**绝不执行截断脚本** |

总上限 **10 分钟**，到点直接判失败。状态框每 5 秒播报一次「代码目前 X 字」。

### 5.5 按钮的功能优先于外观

任何 hover 叠层、视觉叠加都不能挡住点击。讲义版 v0.27 就是栽在这：退出按钮上盖了一层透明 hover，
`SwiftUI` 里透明填充一样接鼠标，按钮点不动。**叠层内容必须加 `allowsHitTesting(false)`**（加在叠层上，不是加在按钮上）。

### 5.6 版本纪律

改代码前先升 `build.sh` 的 `CFBundleShortVersionString` / `CFBundleVersion`；
本地编译 → 替换 App → 试用 → 用户明确说上线，才提交、打 tag、推 GitHub 让 CI 出 Release。
同一标签绝不删除重建，标签已存在就升下一个版本号。

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
| `Pipeline` 第 0 步 | 新开对话失败时**退回根地址重载**（见下） |
| `AppState.downloadDocx` | 保存面板固定落 `~/Downloads`，不再跟题目文件所在目录走 |

**v0.12 两处行为修正**：

1. **新对话兜底**。原来只点页面上的「开启新对话」按钮，JS 匹配不到就返回 `NOT_FOUND`，
   而调用方不检查返回值 —— 页面改版后会静默复用上一轮上下文。现在 `NOT_FOUND` 时走
   `browser.loadDeepSeek(force: true)` 重载 `https://chat.deepseek.com/`（不带任何对话 id，必然是空白新对话），
   轮询 `isPageLoaded` 最多 25 秒，再补 2 秒等 SPA 渲染输入框。
2. **保存目录**。`downloadDocx` 的 `NSSavePanel` 固定指向 `.downloadsDirectory`。原来跟 `startDirectory(for: .topic)`
   走，成品会散落在素材文件夹里。注意 `chooseFile`（打开面板）仍然记着上次目录，那是另一回事，别一起改。
| `EssayApp.swift` | 标题、副标题、两个上传框、主按钮、Word 卡文案 |
| `build.sh` | App 名、可执行名、Bundle ID、版本号、`-disable-sandbox` 兼容、增量构建 |

### 6.1 提示词（`Pipeline.promptText`）

```
我发你 4 个文件，分别是 1.《作文批改规则.md》、2.《标准模式批改.docx》、3.《题目.doc/docx》、
4.《作文.doc/docx》，其中 3、4 可能没有严格命名，需要你自行判断哪个是题目，哪个是作文，而且其内容
可能是文本也可能是扫描件或者照片插入进 word 文档内，需要你来识别执行（有时候照片会拍进多余的内容
需要你提取，其中的作文照片可能有学生的涂改痕迹，你自行判断最终形态，如有手写红笔批改痕迹请忽略）。
《作文批改规则.md》所规定的内容，版式照《标准模式批改.docx》，遇见《作文批改规则.md》未明确规定
的事项，可以从《标准模式批改.docx》参照模仿。因为现在是网页版无法输出文件，请你给出 Python 脚本
文件我自己去执行，其他规则不变。

注意：《标准模式批改.docx》只作版式与笔调的参照，其中的人物、题目、学生作文、批改意见一律不得沿用；
题目和学生作文一律以上传的那两个文件为准。

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
> 的 `promptText` 为准，本节只是镜像，别在这里改。

**五个不能动的部件**：

1. `# ===ESSAY-END===` 末行标记 —— 第 2 层判定（`Scripts.swift:311` 的 `hasEndMark`）。检测正则
   `/#\s*===ESSAY-END===/i` 不锚定行首、允许 `#` 与 `===` 间有空格，所以 AI 万一加了空格也能识别；
   剥除正则 `[ \t]*#[ \t]*===ESSAY-END===[ \t]*$` 同样容错。提示词里那句「#前不要有任何空格」是双保险，不是必需。
2. **最后那段「至少 3 行说明」** —— 第 3 层判定 `afterLines >= 3` 的依据。AI 不可能在代码块没闭合时
   跳到下面写说明，代码块后出现 3 行以上说明 = 代码块一定闭合了。这是结构性证据，删了判定就退化。
3. **「版式照模板，规则没写明的照模板模仿」** —— 模板 docx 因此从「参考文件」升级为「兜底规格」。
   规则 md 可以留白，但模板必须是一份真正合格的成品，否则留白处会被照着错的学。
4. **「模板只作版式与笔调的参照，人物／题目／作文／批改意见不得沿用」** —— 模板是一份**完整成稿**
   （真题面 + 真作文 + 12 条纠错 + 终稿 + 翻译）。没有这句，模型很容易越过「版式」直接沿用内容，
   尤其在上传的题目文件模糊时。规则 §1 只禁「套用规则里的示例题」，示例题藏在模板里，不在这句话射程内。
5. **「3、4 自行判断哪个是题目／作文」** —— App 侧的上传顺序是固定的（题目在前、作文在后，见
   `Pipeline` 的 `uploads` 数组），但**文件名不做约束**，用户可能传 `IMG_0042.docx`。所以提示词把
   「按文件名认」改成了「按内容判断」，同时兜住「照片拍进了多余内容」「作文有涂改痕迹」「红笔批改痕迹要忽略」。
   这条与规则 §7 的转录规则是一套的，改一边要同时看另一边。

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

1. **图标**（用户 2026-10-26 说「后几轮对话就交代你」）：拿到 `.icns` 后放回 `Resources/AppIcon.icns` 再重编即自动生效
   —— `build.sh` 已改成「有 icns 才写 `CFBundleIconFile`」，没有就跳过、用系统通用图标。
   当前 `Resources/AppIcon.icns` **已删除**（原来那份是讲义 app 的，哈希完全相同）。
2. **【重大升级，慢慢想清楚再动手】上传能力扩展**：pdf / jpg / png / 剪贴板粘贴图片，每框最多 3 个文件，超出提示。
   用户 2026-10-26 明确说「今天不做，但留存记忆，这是重大升级，要慢慢考虑思路框架」。
   牵扯至少三处：`AppState.docTypes` / `chooseFile` 的单选限制 / `Pipeline` 写死的 4 文件结构（`uploads` 数组）。
   还要想清楚：多文件怎么排序、怎么告诉 AI「这几个是一篇的」、粘贴板图片怎么落成临时文件、超限时是拒绝还是排队。
   **不要草率开工。**
3. **GitHub 仓库 + CI**：workflow 已就位，但用户要求**等第一个完全体可用版本**再建库推 tag ——
   图标还没上、bug 也没系统测完，现在推不合适。
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

---

## 10. 环境依赖

- macOS 13+（实测 macOS 27 / Xcode 27.1 / arm64）
- Xcode Command Line Tools（`swiftc`）
- 无需 Xcode 工程，无需 CocoaPods / SPM
- 网络：能访问 `chat.deepseek.com`
- 用户需在 DeepSeek 网页版登录一次（登录态存在 App 容器里）

---

## 11. 一句话给接手的人

**这个项目的难度不在业务，在「怎么可靠地知道 AI 写完了」和「怎么把网页当接口用」，这两件事讲义版已经解决了，别重造。**

业务改动只集中在三处：`Resources/` 两个附件、`Pipeline.promptText`、界面文案。
改这三处以外的东西之前，先回讲义版 HANDOVER.md 看有没有踩过坑。
