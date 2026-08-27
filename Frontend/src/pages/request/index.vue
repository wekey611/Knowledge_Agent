<template>
  <div class="my-request-page">
    <header class="my-request-page__head">
      <div>
        <span class="eyebrow">申请</span>
        <h1 class="display-2 my-request-page__title">我的申请</h1>
        <p class="my-request-page__lede">查看你提交的账号申请记录与状态。</p>
      </div>
    </header>

    <div class="info-card">
      <div class="info-card__icon">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10" />
          <path d="M12 8v5M12 16h.01" stroke-linecap="round" />
        </svg>
      </div>
      <div class="info-card__text">
        <h3>功能即将上线</h3>
        <p>查看个人申请记录的接口正在后端开发中。管理员可在「审核」页面处理待审申请。</p>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use '@/styles/tokens' as *;

.my-request-page {
  &__head {
    margin-bottom: $s-6;
    padding-bottom: $s-6;
    border-bottom: 1px solid $border-subtle;
  }
  &__title { margin-top: $s-3; }
  &__lede {
    margin-top: $s-3;
    color: $text-secondary;
    font-size: $fs-15;
    max-width: 460px;
  }
}

.info-card {
  display: flex;
  align-items: flex-start;
  gap: $s-3;
  padding: $s-5;
  background: $bg-surface;
  border: 1px solid $border-subtle;
  border-radius: $r-lg;

  &__icon {
    width: 40px;
    height: 40px;
    border-radius: $r-md;
    background: $info-soft;
    color: $info;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  &__text {
    h3 {
      font-family: $font-body;
      font-weight: $fw-semibold;
      font-size: $fs-15;
      margin-bottom: $s-1;
    }
    p {
      color: $text-secondary;
      font-size: $fs-13;
      line-height: $lh-snug;
    }
  }
}
</style>