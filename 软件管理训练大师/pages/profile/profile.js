// pages/profile/profile.js
const { questionBank } = require('../../utils/data.js');

Page({
  data: {
    userInfo: {},
    favoriteQuestions: [],
    historyQuestions: [],
    totalQuestions: 0,
    completionRate: 0
  },

  onLoad() {
    this.getUserInfo();
  },

  onShow() {
    this.loadData();
  },

  // 获取用户信息
  getUserInfo() {
    const userInfo = wx.getStorageSync('userInfo') || {
      nickName: '微信用户',
      avatarUrl: '/images/default-avatar.png'
    };

    this.setData({ userInfo });
  },

  // 加载数据
  loadData() {
    // 加载收藏的题目
    const favorites = wx.getStorageSync('favorites') || [];
    const favoriteQuestions = questionBank.filter(q => favorites.includes(q.id));

    // 加载历史记录题目
    const history = wx.getStorageSync('history') || [];
    const historyQuestions = questionBank.filter(q => history.includes(q.id));

    // 计算完成率
    const completionRate = history.length > 0
      ? Math.round((history.length / questionBank.length) * 100)
      : 0;

    this.setData({
      favoriteQuestions,
      historyQuestions,
      totalQuestions: questionBank.length,
      completionRate
    });
  },

  // 跳转到指定题目
  goToQuestion(e) {
    const questionId = e.currentTarget.dataset.questionId;

    // 切换到题库页面
    wx.switchTab({
      url: '/pages/question/question',
      success: () => {
        // 延迟发送事件，确保页面已经加载
        setTimeout(() => {
          // 通过事件通信跳转到指定题目
          const pages = getCurrentPages();
          const questionPage = pages.find(page => page.route === 'pages/question/question');
          if (questionPage && questionPage.scrollToQuestion) {
            questionPage.scrollToQuestion(questionId);
          }
        }, 100);
      }
    });
  },

  // 清除收藏
  clearFavorites() {
    wx.showModal({
      title: '确认清除',
      content: '确定要清除所有收藏记录吗？',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('favorites');
          this.setData({
            favoriteQuestions: [],
            completionRate: Math.round((this.data.historyQuestions.length / questionBank.length) * 100)
          });
          wx.showToast({
            title: '已清除收藏',
            icon: 'success'
          });
        }
      }
    });
  },

  // 清除历史记录
  clearHistory() {
    wx.showModal({
      title: '确认清除',
      content: '确定要清除所有历史记录吗？',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('history');
          this.setData({
            historyQuestions: [],
            completionRate: 0
          });
          wx.showToast({
            title: '已清除历史',
            icon: 'success'
          });
        }
      }
    });
  }
});