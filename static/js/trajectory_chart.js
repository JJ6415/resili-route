/**
 * ResiliRoute Tri-Line Trajectory Canvas Renderer
 * Renders the 3-line comparative series and dynamic shaded polygon areas (Emerald Savings / Cyan Risk Reduction).
 */
class TrajectoryChart {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.data = null;
    this.resize();
    window.addEventListener('resize', () => this.resize());
  }

  resize() {
    if (!this.canvas) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width * window.devicePixelRatio;
    this.canvas.height = rect.height * window.devicePixelRatio;
    this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    this.render();
  }

  updateData(trajectoryData) {
    this.data = trajectoryData;
    this.render();
  }

  render() {
    if (!this.canvas || !this.data) return;
    const ctx = this.ctx;
    const width = this.canvas.width / window.devicePixelRatio;
    const height = this.canvas.height / window.devicePixelRatio;

    ctx.clearRect(0, 0, width, height);

    const padLeft = 50;
    const padRight = 30;
    const padTop = 30;
    const padBottom = 40;
    const chartW = width - padLeft - padRight;
    const chartH = height - padTop - padBottom;

    const labels = this.data.x_axis_labels || [];
    const n = labels.length;
    if (n < 2) return;

    // Calculate Y scale
    const l1 = this.data.line1_values || [];
    const l2 = this.data.line2_values || [];
    const l3 = this.data.line3_values || [];
    const allVals = [...l1, ...l2, ...l3];
    const minVal = Math.min(...allVals) * 0.9;
    const maxVal = Math.max(...allVals) * 1.1;

    const getX = (idx) => padLeft + (idx / (n - 1)) * chartW;
    const getY = (val) => padTop + chartH - ((val - minVal) / (maxVal - minVal)) * chartH;

    // 1. Draw Grid Lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let i = 0; i < 5; i++) {
      const y = padTop + (i / 4) * chartH;
      ctx.moveTo(padLeft, y);
      ctx.lineTo(width - padRight, y);
      const val = maxVal - (i / 4) * (maxVal - minVal);
      ctx.fillStyle = '#64748b';
      ctx.font = '10px monospace';
      ctx.textAlign = 'right';
      ctx.fillText(val.toFixed(1), padLeft - 8, y + 3);
    }
    ctx.stroke();

    // Draw X labels
    ctx.textAlign = 'center';
    for (let i = 0; i < n; i++) {
      const x = getX(i);
      ctx.fillStyle = '#94a3b8';
      ctx.font = '10px sans-serif';
      ctx.fillText(labels[i], x, height - 15);
    }

    // 2. Shaded Polygon Area (between Line 2 and Line 3)
    if (l2.length === n && l3.length === n) {
      ctx.beginPath();
      // Forward along Line 2
      ctx.moveTo(getX(0), getY(l2[0]));
      for (let i = 1; i < n; i++) {
        ctx.lineTo(getX(i), getY(l2[i]));
      }
      // Backward along Line 3
      for (let i = n - 1; i >= 0; i--) {
        ctx.lineTo(getX(i), getY(l3[i]));
      }
      ctx.closePath();

      if (this.data.shading_type === 'EMERALD_SAVINGS') {
        const grad = ctx.createLinearGradient(0, padTop, 0, height);
        grad.addColorStop(0, 'rgba(16, 185, 129, 0.35)');
        grad.addColorStop(1, 'rgba(16, 185, 129, 0.05)');
        ctx.fillStyle = grad;
      } else {
        const grad = ctx.createLinearGradient(0, padTop, 0, height);
        grad.addColorStop(0, 'rgba(6, 182, 212, 0.40)');
        grad.addColorStop(1, 'rgba(6, 182, 212, 0.05)');
        ctx.fillStyle = grad;
      }
      ctx.fill();
    }

    // 3. Draw Lines
    const drawSeries = (values, color, isDashed = false) => {
      ctx.beginPath();
      ctx.strokeStyle = color;
      ctx.lineWidth = 2.5;
      if (isDashed) {
        ctx.setLineDash([5, 4]);
      } else {
        ctx.setLineDash([]);
      }
      for (let i = 0; i < values.length; i++) {
        const x = getX(i);
        const y = getY(values[i]);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
      ctx.setLineDash([]);

      // Draw dots
      for (let i = 0; i < values.length; i++) {
        const x = getX(i);
        const y = getY(values[i]);
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
        ctx.strokeStyle = '#0f172a';
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }
    };

    drawSeries(l1, this.data.line1_color || '#64748b', true);
    drawSeries(l2, this.data.line2_color || '#ef4444', false);
    drawSeries(l3, this.data.line3_color || '#10b981', false);
  }
}

window.TrajectoryChart = TrajectoryChart;
