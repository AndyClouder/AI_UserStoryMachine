# 工作流应该是什么样子的？

它应该是一个图，所以，用代码？Temporal 工作流是命令式编写的。命令式外壳，函数式核心... 这在这里很有道理。这是一个无状态的工作流。整体和部分的状态在进展中不断变化。

理想情况下它应该是并发的，尽可能独立地并行处理故事。然后也需要一些协调，来等待/汇集线程。一开始，我们可以串行做，只是为了保持简单。并行主要是为了性能和真实的表示。这个可以等等。

```python
inputs = [PRD, ERD, Repo]

stories = [] # 输出是一个故事列表，但我们在迭代它们，随着进展不断改进它们。
response = (nil, nil) # (approved/rejected, comment) 元组，包含批准状态和可选评论
feedback = nil

relevant_files = find_relevant_files(inputs)
while true:
  prd_erd_questions = understand_prd_erd_and_ask_questions(inputs, response.comment)
  response = get_human_input(prd_questions)
  if response.rejected?
    continue to iterate on understanding inputs
  else
    break


while true: ## 切割板
  stories = problem_break_down(inputs, stories, feedback) # 小型、独立、有价值、可验证的，带有基本的 T 恤尺码估算
  feedback = get_human_input(stories)
  if iteration_needed?(feedback)
    continue to iterate on stories with feedback
  else
    break


for each story in stories:
  story.define_acceptance_criteria(inputs)
  story.enrich_context(inputs)
  story.add_implementation_context(inputs)
  story.estimate(inputs)
  internal_feedback = story.is_ready_for_implementation?
  if(internal_feedback.approved?)
    response = get_human_input(story)
    if response.approved?
      next
    else
      iterate with response.comments
  else
    iterate with internal_feedback.comments

self_eval_result =
  do_stories_add_up_to_prd_acs(stories)
  + are_stories_small(stories)
```

# 组织工作
## 已优先处理的 TODO
- [c] 添加单元测试

## 来自提示调整和故事列表迭代的一些笔记：
- 反思部分似乎有助于提醒所有指令
- 对话中的迭代速度非常重要

### 接口
- 反馈需要针对多个故事或各种事情给出。如果能够对每个故事或故事列表发表评论会很棒。
- 至少需要在 CLI 中启用多行反馈。
- 故事编号对于引用很有用：故事 7 应该被分解/降低优先级
- 一些保证其他故事不会退化的保证将很有用。
- 看到每次迭代的"改变了什么"会很有用
- 喜欢拖放重排序，并在迭代时保持该顺序
- 一些故事分组似乎很好，比如分析、导入等。小型史诗。使用故事前缀就可以。

### 功能
- 大多数评论需要被解释为对故事的操作。需要调整提示以反映这一点。
- 虚假的评论反正也能工作，理想情况下应该要求澄清。对话语义已经存在于响应 API 中。如何利用这一点？工具需要区分对话响应和故事输出
- 工作流可以使用时序风格的状态持久化来继续对话等。

## 接口想法
- 与 JIRA 集成
- 构建分步定制工作流接口