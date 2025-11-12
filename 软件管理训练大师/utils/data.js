// 模拟题库数据
const questionBank = [
  {
    id: 1,
    title: "JavaScript中，以下哪个方法可以向数组末尾添加元素？",
    options: ["push()", "pop()", "shift()", "unshift()"],
    answer: 0,
    explanation: "push()方法可以向数组末尾添加一个或多个元素"
  },
  {
    id: 2,
    title: "在CSS中，以下哪个属性用于设置元素的背景颜色？",
    options: ["color", "background-color", "background", "bg-color"],
    answer: 1,
    explanation: "background-color属性用于设置元素的背景颜色"
  },
  {
    id: 3,
    title: "HTML5中新增的语义化标签是？",
    options: ["<div>", "<span>", "<header>", "<table>"],
    answer: 2,
    explanation: "<header>是HTML5中新增的语义化标签，用于表示页面或区域的页眉"
  },
  {
    id: 4,
    title: "在JavaScript中，typeof null的结果是什么？",
    options: ["null", "undefined", "object", "string"],
    answer: 2,
    explanation: "在JavaScript中，typeof null返回'object'，这是一个历史遗留的bug"
  },
  {
    id: 5,
    title: "React中，用于管理组件状态的Hook是？",
    options: ["useEffect", "useState", "useContext", "useReducer"],
    answer: 1,
    explanation: "useState是React中最基本的Hook，用于在函数组件中添加状态"
  },
  {
    id: 6,
    title: "HTTP状态码404表示什么？",
    options: ["服务器错误", "请求成功", "资源未找到", "重定向"],
    answer: 2,
    explanation: "HTTP 404状态码表示请求的资源未找到"
  },
  {
    id: 7,
    title: "在Git中，哪个命令用于查看提交历史？",
    options: ["git status", "git log", "git diff", "git add"],
    answer: 1,
    explanation: "git log命令用于查看提交历史记录"
  },
  {
    id: 8,
    title: "Python中，以下哪个是正确的函数定义？",
    options: [
      "function myFunc():",
      "def myFunc():",
      "func myFunc() {}",
      "define myFunc():"
    ],
    answer: 1,
    explanation: "Python中使用def关键字定义函数，语法为def function_name():"
  },
  {
    id: 9,
    title: "在数据库中，用于查询数据的关键字是？",
    options: ["INSERT", "UPDATE", "SELECT", "DELETE"],
    answer: 2,
    explanation: "SELECT关键字用于从数据库中查询数据"
  },
  {
    id: 10,
    title: "Vue.js中，用于条件渲染的指令是？",
    options: ["v-show", "v-if", "v-for", "v-model"],
    answer: 1,
    explanation: "v-if是Vue.js中的条件渲染指令，根据条件决定是否渲染元素"
  },
  {
    id: 11,
    title: "在JavaScript中，Promise的三种状态是？",
    options: [
      "pending、fulfilled、rejected",
      "waiting、success、failed",
      "start、running、end",
      "init、processing、complete"
    ],
    answer: 0,
    explanation: "Promise有三种状态：pending（进行中）、fulfilled（已成功）、rejected（已失败）"
  },
  {
    id: 12,
    title: "CSS中，以下哪个选择器优先级最高？",
    options: [
      "元素选择器",
      "类选择器",
      "ID选择器",
      "内联样式"
    ],
    answer: 3,
    explanation: "内联样式的优先级最高，其次是ID选择器、类选择器、元素选择器"
  }
];

module.exports = {
  questionBank
};