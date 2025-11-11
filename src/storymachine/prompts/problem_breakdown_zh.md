<task>
从以下源材料中，通过 `create_stories` 工具生成用户故事列表。
</task>

<sources>
<project_requirements_document>
{prd_content}
</project_requirements_document>
<technical_specification_document>
{tech_spec_content}
</technical_specification_document>
<repository_context>
{repo_context}
</repository_context>
</sources>

<breakdown>
- 阅读产品需求文档和技术规范文档，将问题分解成更小的部分。
- 较小的部分应该让开发者更容易处理和理解。
- 如果问题是 CRUD 类的，为每个命令或查询创建部分。
- 尽可能，每个部分也应该对业务有价值。
- 一个部分对应一个价值。
- 每个部分应该结构化为用户故事，提及 <角色>、<能力> 和 <收益>。
- 查看所有故事，然后为故事添加相对估算到以下之一：[XS]/[S]/[M]/[L]，并添加为前缀。
- 按应该实现的顺序对故事进行排序。
</breakdown>

<reflection>
在输出前内部检查：
1) 覆盖范围：源材料中每个面向用户的能力和验收测试都恰好出现在一个故事（或明确分割的一对）中，没有空白。
2) 角色：每个标题使用源材料中的真实最终用户角色。
3) 标题：陈述能力和收益。
4) 估算：每个故事都有 T 恤尺码估算前缀
5) AC：行为性、可测试、基于源材料；在指定时包含权限。
6) 没有重复/重叠；根据需要拆分或合并以满足 INVEST 原则。
不要输出此反思。
</reflection>