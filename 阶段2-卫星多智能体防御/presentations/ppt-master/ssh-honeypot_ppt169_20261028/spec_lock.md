<!-- ppt-master-schema: spec-lock/v1 -->
# Execution Lock

## canvas
- viewBox: 0 0 1280 720
- format: PPT 16:9

## communication
- primary_language: zh-CN
- audience: 导师；熟悉 LLM 与 Agent 安全，本次主要检验我是否真正读懂一篇论文
- objective: 把 ICML 2026 的 Speculative Safety Honeypot 讲透，让导师确认核心研究问题能一句话说清、四张图能指着讲、术语与数字不出错
- core_message: 这篇论文不问“你已经做了什么”，问“你接下来会做什么”；它的优势不是多了一层检测，而是让检测器不必那么准也行
- consumption_mode: balanced

## mode
- mode: custom
- mode_references: instructional
- mode_behavior: 拆解再排序：先立两类威胁与两个问题，再依次拆开动机场景、架构、三处关键设计，最后落到证据与边界；每页只承担一个讲解步骤，同类概念用同形结构并列；标题直说这页讲什么；关键术语第一次出现时先定义再用，每处设计都点出它的代价。

## visual_style
- visual_style: custom
- visual_style_references: swiss-minimal
- visual_style_behavior: 冷峻技术页：纯白底、无渐变无阴影；标题炭黑大字配一条 48 px 青色短杠；强调只出现在两个位置——青色给方法与结论，焦橙给风险与代价；论文原图直放，不加边框、底色与投影；页脚只有一条发丝分隔线和页码。

## colors
- background: #FFFFFF
- secondary_bg: #F4F6F7
- primary: #16202A
- accent: #0E8A7D
- secondary_accent: #C2410C
- body_text: #1F2933
- secondary_text: #5E6B75
- divider: #DDE2E6

## typography
- title_family: Microsoft YaHei, Arial, sans-serif
- body_family: Microsoft YaHei, Arial, sans-serif
- font_family: Microsoft YaHei, Arial, sans-serif
- body: 24
- title: 42
- subtitle: 32
- lead: 28
- annotation: 18
- footnote: 16
- display: 64

## icons
- library: tabler-outline
- stroke_width: 2
- inventory: tabler-outline/mail, tabler-outline/user, tabler-outline/robot, tabler-outline/tool, tabler-outline/binary-tree, tabler-outline/scissors, tabler-outline/filter, tabler-outline/alert-triangle, tabler-outline/arrow-right, tabler-outline/check, tabler-outline/x, tabler-outline/settings

## images
- fig1: images/ssh-fig1.png | source=user | crop=no-crop
- fig2: images/ssh-fig2.png | source=user | crop=no-crop
- fig3: images/ssh-fig3.png | source=user | crop=no-crop
- fig4: images/ssh-fig4.png | source=user | crop=no-crop

## page_rhythm
- P01: anchor
- P02: breathing
- P03: dense
- P04: dense
- P05: breathing
- P06: dense
- P07: anchor
- P08: dense
- P09: dense

## pptx_structure
- mode: flat

## page_visualizations
- P08: table/comparison_matrix

## forbidden
- `mask`, `<style>`, `class`, external CSS, `<foreignObject>`, `textPath`, `@font-face`, `<animate*>`, `<set>`, `<script>` / event attributes, `<iframe>`
- HTML named entities in text; write typography as raw Unicode and escape XML reserved characters
- 不引入图库图或生成图 (user)
- 不给论文原图加边框、底色、投影或裁切 (user)
