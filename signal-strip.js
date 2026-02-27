(function() {
  const svg = document.querySelector('.strip-svg');
  if (!svg) return;

  const rows = 10, startY = 5, rowH = 5, maxA = 15;
  const amps = [0, 1.5, 4, 8, 12, 15, 12, 8, 4, 0];
  const bx  = [400,402,397,404,407,400,396,403,399,400];
  const bx2 = [195,197,193,199,202,196,192,198,195,195];
  const bx3 = [605,607,602,609,612,605,601,608,604,605];

  function rowColor(A) {
    const t = Math.min(A / maxA, 1);
    return 'rgb(' + Math.round(153+26*t) + ',' + Math.round(2+3*t) + ',' + Math.round(2+3*t) + ')';
  }

  const pls = [], rowY = [];
  const sw1 = amps.map(A => 2 * Math.pow(80 + A * 1.6, 2));
  const sw2 = amps.map(A => 2 * Math.pow(55 + A, 2));
  const sw3 = amps.map(A => 2 * Math.pow(60 + A, 2));

  for (let i = 0; i < rows; i++) {
    const A = amps[i];
    const pl = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    pl.setAttribute('stroke', rowColor(A));
    pl.setAttribute('stroke-width', A > 10 ? '0.9' : A > 3 ? '0.6' : '0.4');
    pl.setAttribute('fill', 'none');
    pl.setAttribute('opacity', String(A > 10 ? 0.88 : A > 3 ? 0.55 : 0.25));
    svg.appendChild(pl);
    pls.push(pl);
    rowY.push(startY + i * rowH);
  }

  let t = 0;
  function tick() {
    t += 0.0022;
    for (let i = 0; i < rows; i++) {
      const A = amps[i];
      if (A === 0) { pls[i].setAttribute('points', '0,' + rowY[i] + ' 800,' + rowY[i]); continue; }
      const drift = Math.sin(t + i * 0.20) * (4 + A * 0.05);
      const c  = bx[i]  + drift,  c2 = bx2[i] + drift * 0.6,  c3 = bx3[i] + drift * 0.6;
      const pts = [];
      for (let x = 0; x <= 800; x += 5) {
        const g  = A      * Math.exp(-Math.pow(x-c,  2) / sw1[i]);
        const s1 = A*0.42 * Math.exp(-Math.pow(x-c2, 2) / sw2[i]);
        const s2 = A*0.35 * Math.exp(-Math.pow(x-c3, 2) / sw3[i]);
        pts.push(x + ',' + (rowY[i] - g - s1 - s2).toFixed(1));
      }
      pls[i].setAttribute('points', pts.join(' '));
    }
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})();
