class Component extends DCLogic {
  state = { now: Date.now(), tab: 'wish' };

  componentDidMount() {
    this.timer = setInterval(() => this.setState({ now: Date.now() }), 1000);
  }
  componentWillUnmount() {
    clearInterval(this.timer);
  }

  wavyFrame() {
    const x0 = 26, y0 = 26, x1 = 974, y1 = 1274, step = 46, amp = 14;
    let dir = 1;
    let d = `M ${x0} ${y0}`;
    for (let x = x0; x < x1; x += step) { const nx = Math.min(x + step, x1); d += ` Q ${(x + nx) / 2} ${y0 + dir * amp} ${nx} ${y0}`; dir = -dir; }
    for (let y = y0; y < y1; y += step) { const ny = Math.min(y + step, y1); d += ` Q ${x1 + dir * amp} ${(y + ny) / 2} ${x1} ${ny}`; dir = -dir; }
    for (let x = x1; x > x0; x -= step) { const nx = Math.max(x - step, x0); d += ` Q ${(x + nx) / 2} ${y1 + dir * amp} ${nx} ${y1}`; dir = -dir; }
    for (let y = y1; y > y0; y -= step) { const ny = Math.max(y - step, y0); d += ` Q ${x0 + dir * amp} ${(y + ny) / 2} ${x0} ${ny}`; dir = -dir; }
    return d + ' Z';
  }

  renderVals() {
    const target = new Date(this.props.countdownTarget ?? '2026-07-17T18:00:00+03:00').getTime();
    let diff = Math.max(0, target - this.state.now);
    const days = Math.floor(diff / 86400000); diff -= days * 86400000;
    const hours = Math.floor(diff / 3600000); diff -= hours * 3600000;
    const mins = Math.floor(diff / 60000); diff -= mins * 60000;
    const secs = Math.floor(diff / 1000);
    const pad = (n) => String(n).padStart(2, '0');

    const tab = this.state.tab;
    const active = ['#2853C6', '#F4EEE3'];
    const idle = ['transparent', '#2853C6'];
    const [wishBg, wishFg] = tab === 'wish' ? active : idle;
    const [rulesBg, rulesFg] = tab === 'rules' ? active : idle;
    const [bringBg, bringFg] = tab === 'bring' ? active : idle;

    return {
      framePath: this.wavyFrame(),
      showCountdown: this.props.showCountdown ?? true,
      cdDays: String(days), cdHours: pad(hours), cdMins: pad(mins), cdSecs: pad(secs),
      gallerySlots: Array.from({ length: 8 }, (_, i) => ({ id: 'gallery-' + (i + 1), label: 'Момент ' + (i + 1), rot: [-1.6, 1.2, -0.8, 1.8, -1.2, 0.9, -1.8, 1.4][i % 8] })),
      showWish: tab === 'wish', showRules: tab === 'rules', showBring: tab === 'bring',
      goWish: () => this.setState({ tab: 'wish' }),
      goRules: () => this.setState({ tab: 'rules' }),
      goBring: () => this.setState({ tab: 'bring' }),
      tabWishBg: wishBg, tabWishFg: wishFg,
      tabRulesBg: rulesBg, tabRulesFg: rulesFg,
      tabBringBg: bringBg, tabBringFg: bringFg,
    };
  }
}
