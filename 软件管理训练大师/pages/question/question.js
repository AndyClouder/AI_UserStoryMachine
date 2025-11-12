// pages/question/question.js
const { questionBank } = require('../../utils/data.js');

Page({
  data: {
    questions: [],
    filteredQuestions: [],
    searchKeyword: '',
    selectedAnswers: {},
    showAnswer: {},
    favorites: [],
    history: []
  },

  onLoad() {
    this.loadData();
  },

  onShow() {
    // 每次显示页面时刷新数据
    this.loadData();
  },

  loadData() {
    // 加载题库数据
    this.setData({
      questions: questionBank,
      filteredQuestions: questionBank
    });

    // 加载收藏数据
    const favorites = wx.getStorageSync('favorites') || [];
    this.setData({ favorites });

    // 加载历史记录
    const history = wx.getStorageSync('history') || [];
    this.setData({ history });
  },

  // 搜索输入
  onSearchInput(e) {
    const keyword = e.detail.value;
    this.setData({ searchKeyword: keyword });
    this.filterQuestions(keyword);
  },

  // 搜索
  onSearch() {
    this.filterQuestions(this.data.searchKeyword);
  },

  // 过滤题目
  filterQuestions(keyword) {
    if (!keyword.trim()) {
      this.setData({
        filteredQuestions: this.data.questions
      });
      return;
    }

    const filtered = this.data.questions.filter(question => {
      return question.title.toLowerCase().includes(keyword.toLowerCase()) ||
             question.options.some(option =>
               option.toLowerCase().includes(keyword.toLowerCase())
             );
    });

    this.setData({
      filteredQuestions: filtered
    });
  },

  // 选择选项
  selectOption(e) {
    const { questionId, optionIndex } = e.currentTarget.dataset;
    const selectedAnswers = { ...this.data.selectedAnswers };
    selectedAnswers[questionId] = optionIndex;

    this.setData({ selectedAnswers });

    // 记录到历史记录
    this.addToHistory(questionId);
  },

  // 显示/隐藏答案
  showAnswer(e) {
    const { questionId } = e.currentTarget.dataset;
    const showAnswer = { ...this.data.showAnswer };
    showAnswer[questionId] = !showAnswer[questionId];

    this.setData({ showAnswer });

    // 记录到历史记录
    this.addToHistory(questionId);
  },

  // 切换收藏状态
  toggleFavorite(e) {
    const { questionId } = e.currentTarget.dataset;
    let favorites = [...this.data.favorites];

    const index = favorites.indexOf(questionId);
    if (index > -1) {
      // 取消收藏
      favorites.splice(index, 1);
      wx.showToast({
        title: '已取消收藏',
        icon: 'none'
      });
    } else {
      // 添加收藏
      favorites.push(questionId);
      wx.showToast({
        title: '已收藏',
        icon: 'success'
      });
    }

    this.setData({ favorites });
    wx.setStorageSync('favorites', favorites);
  },

  // 检查是否已收藏
  isFavorite(questionId) {
    return this.data.favorites.includes(questionId);
  },

  // 添加到历史记录
  addToHistory(questionId) {
    let history = [...this.data.history];

    // 移除已存在的记录
    const existingIndex = history.indexOf(questionId);
    if (existingIndex > -1) {
      history.splice(existingIndex, 1);
    }

    // 添加到开头
    history.unshift(questionId);

    // 限制历史记录数量
    if (history.length > 50) {
      history = history.slice(0, 50);
    }

    this.setData({ history });
    wx.setStorageSync('history', history);
  },

  // 滚动到指定题目
  scrollToQuestion(questionId) {
    const index = this.data.filteredQuestions.findIndex(q => q.id === questionId);
    if (index !== -1) {
      // 滚动到指定题目
      wx.pageScrollTo({
        scrollTop: index * 400, // 大概每个题目卡片的高度
        duration: 300
      });

      // 高亮显示该题目
      wx.showToast({
        title: `已跳转到题目 ${index + 1}`,
        icon: 'none'
      });
    }
  }
});