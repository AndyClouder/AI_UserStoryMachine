<task>
从以下源材料中，生成用户故事列表。请以JSON格式返回结果，包含"stories"数组。
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
- 阅读产品需求文档和技术规范文档，将问题分解成更小的部分
- 较小的部分应该让开发者更容易处理和理解
- 如果问题是CRUD类，为每个命令或查询创建部分
- 每个部分应该对业务有价值，一个部分对应一个价值
- 每个部分应该结构化为用户故事，提及角色、能力和收益
- 为故事添加相对估算：[XS]/[S]/[M]/[L]，作为前缀
- 按实现顺序对故事进行排序
</breakdown>

<output_format>
请严格按照以下JSON格式返回结果：

```json
{{
  "stories": [
    {{
      "title": "[估算] 用户故事标题 - 描述角色、能力和收益",
      "acceptance_criteria": [
        "验收标准1：具体的、可测试的行为",
        "验收标准2：另一个具体的、可测试的行为"
      ],
      "enriched_context": "从PRD和技术规范中提取的详细上下文信息"
    }}
  ]
}}
```

重要提示：
1. 必须返回有效的JSON格式
2. title字段以估算前缀开始，如"[S] 用户登录功能"
3. acceptance_criteria必须是字符串数组
4. enriched_context提供详细实现信息
5. 至少生成3-8个用户故事
</output_format>

<reflection>
在输出前内部检查：
1) 覆盖范围：源材料中每个面向用户的能力都出现在一个故事中
2) 角色：每个标题使用真实的最终用户角色
3) 标题：清晰陈述能力和收益
4) 估算：每个故事都有T恤尺码估算前缀
5) AC：行为性、可测试、基于源材料
6) 没有重复/重叠

不要输出此反思，直接返回JSON格式的故事列表。
</reflection>