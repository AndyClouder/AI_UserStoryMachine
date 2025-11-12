// app.js
App({
  onLaunch() {
    // 初始化本地存储
    this.initStorage();
  },

  initStorage() {
    // 初始化收藏数据
    if (!wx.getStorageSync('favorites')) {
      wx.setStorageSync('favorites', []);
    }

    // 初始化历史记录数据
    if (!wx.getStorageSync('history')) {
      wx.setStorageSync('history', []);
    }

    // 初始化用户信息
    if (!wx.getStorageSync('userInfo')) {
      wx.setStorageSync('userInfo', {
        nickName: '微信用户',
        avatarUrl: '/images/default-avatar.svg'
      });
    }
  },

  globalData: {
    userInfo: null
  }
})