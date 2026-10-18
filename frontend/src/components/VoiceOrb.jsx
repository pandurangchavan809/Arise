import React, { useRef, useEffect, useCallback } from 'react';

/**
 * VoiceOrb — Animated liquid crystal waveform orb for the voice assistant.
 *
 * States:
 *   idle       → gentle breathing pulse, soft glow
 *   listening  → expanding reactive waves, bright teal
 *   processing → spinning orbital rings, amber/gold
 *   speaking   → pulsing outward waves synchronized with speech
 *
 * Renders on a <canvas> element using requestAnimationFrame.
 */
export default function VoiceOrb({ state = 'idle', audioLevel = 0, size = 320 }) {
  const canvasRef = useRef(null);
  const frameRef = useRef(null);
  const timeRef = useRef(0);

  const draw = useCallback(
    (ctx, width, height, t) => {
      ctx.clearRect(0, 0, width, height);
      const cx = width / 2;
      const cy = height / 2;
      const baseRadius = Math.min(cx, cy) * 0.32;

      // ── Color Palettes per state ──
      const palettes = {
        idle: ['rgba(0,210,211,', 'rgba(0,180,220,', 'rgba(0,150,200,'],
        listening: ['rgba(0,245,245,', 'rgba(0,220,255,', 'rgba(80,200,255,'],
        processing: ['rgba(255,190,60,', 'rgba(255,160,40,', 'rgba(255,130,20,'],
        speaking: ['rgba(100,240,220,', 'rgba(60,220,255,', 'rgba(0,200,240,'],
      };
      const colors = palettes[state] || palettes.idle;

      // ── Background radial glow ──
      const glowAlpha = state === 'idle' ? 0.08 : state === 'listening' ? 0.18 : state === 'processing' ? 0.12 : 0.15;
      const glowPulse = 1 + Math.sin(t * 0.8) * 0.15;
      const grd = ctx.createRadialGradient(cx, cy, baseRadius * 0.3, cx, cy, baseRadius * 3 * glowPulse);
      grd.addColorStop(0, `${colors[0]}${glowAlpha})`);
      grd.addColorStop(0.5, `${colors[1]}${glowAlpha * 0.4})`);
      grd.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = grd;
      ctx.fillRect(0, 0, width, height);

      // ── Number of waveform layers ──
      const layerCount = state === 'idle' ? 5 : state === 'listening' ? 7 : state === 'processing' ? 6 : 7;

      for (let layer = 0; layer < layerCount; layer++) {
        const layerRatio = layer / layerCount;
        const alpha = 0.12 + (1 - layerRatio) * 0.35;

        // Dynamic radius modifiers per state
        let radiusMod = 1;
        let speedMod = 1;
        let amplitudeMod = 1;

        if (state === 'idle') {
          radiusMod = 1 + Math.sin(t * 0.5 + layer * 0.7) * 0.06;
          speedMod = 0.4 + layerRatio * 0.3;
          amplitudeMod = 0.4;
        } else if (state === 'listening') {
          const audioBoost = 1 + audioLevel * 2.5;
          radiusMod = 1 + Math.sin(t * 1.2 + layer * 0.9) * 0.15 * audioBoost;
          speedMod = 0.8 + audioLevel * 1.5;
          amplitudeMod = 0.8 + audioLevel * 1.2;
        } else if (state === 'processing') {
          radiusMod = 1 + Math.sin(t * 2.5 + layer * 1.2) * 0.1;
          speedMod = 1.5 + layerRatio * 0.8;
          amplitudeMod = 0.6;
        } else if (state === 'speaking') {
          const speechPulse = Math.sin(t * 3 + layer * 0.5) * 0.5 + 0.5;
          radiusMod = 1 + speechPulse * 0.12 + audioLevel * 0.3;
          speedMod = 1.0 + audioLevel * 0.8;
          amplitudeMod = 0.7 + audioLevel * 0.8;
        }

        const r = baseRadius * (0.7 + layerRatio * 0.8) * radiusMod;
        const points = 180;
        const colorIdx = layer % colors.length;

        ctx.beginPath();
        ctx.strokeStyle = `${colors[colorIdx]}${alpha})`;
        ctx.lineWidth = 1.2 + (1 - layerRatio) * 1.5;
        ctx.shadowColor = `${colors[colorIdx]}0.3)`;
        ctx.shadowBlur = state === 'idle' ? 8 : 16;

        for (let i = 0; i <= points; i++) {
          const angle = (i / points) * Math.PI * 2;

          // Multiple frequency waveform distortions
          const wave1 = Math.sin(angle * 3 + t * speedMod + layer * 0.8) * 12 * amplitudeMod;
          const wave2 = Math.sin(angle * 5 - t * speedMod * 0.7 + layer * 1.3) * 6 * amplitudeMod;
          const wave3 = Math.sin(angle * 7 + t * speedMod * 1.3) * 3 * amplitudeMod;
          const wave4 = Math.cos(angle * 2 - t * 0.3 + layer * 2.1) * 8 * amplitudeMod;

          const totalDisplacement = wave1 + wave2 + wave3 + wave4;
          const currentR = r + totalDisplacement;

          const x = cx + Math.cos(angle) * currentR;
          const y = cy + Math.sin(angle) * currentR;

          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }

        ctx.closePath();
        ctx.stroke();
      }

      // ── Inner core glow ──
      const coreRadius = baseRadius * 0.25;
      const corePulse = 1 + Math.sin(t * 1.5) * 0.15;
      const coreGrd = ctx.createRadialGradient(cx, cy, 0, cx, cy, coreRadius * corePulse);

      if (state === 'processing') {
        coreGrd.addColorStop(0, 'rgba(255,200,80,0.4)');
        coreGrd.addColorStop(0.6, 'rgba(255,160,40,0.15)');
        coreGrd.addColorStop(1, 'rgba(255,130,20,0)');
      } else {
        coreGrd.addColorStop(0, 'rgba(0,230,230,0.35)');
        coreGrd.addColorStop(0.6, 'rgba(0,200,220,0.1)');
        coreGrd.addColorStop(1, 'rgba(0,180,200,0)');
      }

      ctx.fillStyle = coreGrd;
      ctx.beginPath();
      ctx.arc(cx, cy, coreRadius * corePulse, 0, Math.PI * 2);
      ctx.fill();

      // ── Particle sparkles (listening/speaking) ──
      if (state === 'listening' || state === 'speaking') {
        const particleCount = 12 + Math.floor(audioLevel * 20);
        for (let i = 0; i < particleCount; i++) {
          const pAngle = (i / particleCount) * Math.PI * 2 + t * 0.3;
          const pDist = baseRadius * (1.1 + Math.sin(t * 2 + i * 1.7) * 0.4);
          const pAlpha = 0.3 + Math.sin(t * 3 + i) * 0.3;
          const pSize = 1 + Math.sin(t * 2.5 + i * 0.9) * 0.8;
          const px = cx + Math.cos(pAngle) * pDist;
          const py = cy + Math.sin(pAngle) * pDist;

          ctx.beginPath();
          ctx.fillStyle = `rgba(0,240,240,${pAlpha})`;
          ctx.arc(px, py, pSize, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      ctx.shadowBlur = 0;
    },
    [state, audioLevel]
  );

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const dpr = window.devicePixelRatio || 1;
    canvas.width = size * dpr;
    canvas.height = size * dpr;
    canvas.style.width = `${size}px`;
    canvas.style.height = `${size}px`;

    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);

    let running = true;
    const loop = () => {
      if (!running) return;
      timeRef.current += 0.016;
      draw(ctx, size, size, timeRef.current);
      frameRef.current = requestAnimationFrame(loop);
    };
    loop();

    return () => {
      running = false;
      if (frameRef.current) cancelAnimationFrame(frameRef.current);
    };
  }, [size, draw]);

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none select-none"
      style={{ width: size, height: size }}
    />
  );
}
