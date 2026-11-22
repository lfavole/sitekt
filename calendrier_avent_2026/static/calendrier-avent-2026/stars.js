/**
 * Effet visuel Canvas haute performance (120+ FPS) :
 * - Traînée lumineuse et étincelles au survol de la souris / tactile
 * - Flocons cristallins à 6 branches pré-rendus en mémoire
 * - Champ de force répulsif autour du curseur ET de l'élément HTML actuellement focalisé (Tab / clic)
 * - Cycle météorologique dynamique alternant temps calme et tempêtes de neige venteuses
 */
window.addEventListener("DOMContentLoaded", function () {
  // 1. Création et configuration du Canvas plein écran
  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d", { alpha: true });
  Object.assign(canvas.style, {
    position: "fixed",
    top: "0",
    left: "0",
    width: "100vw",
    height: "100vh",
    pointerEvents: "none",
    zIndex: "9999"
  });
  document.body.appendChild(canvas);

  let dpr = window.devicePixelRatio || 1;
  const resize = () => {
    dpr = window.devicePixelRatio || 1;
    canvas.width = window.innerWidth * dpr;
    canvas.height = window.innerHeight * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  };
  window.addEventListener("resize", resize);
  resize();

  // 2. Configuration générale
  const config = {
    // Souris & Étoiles
    starDuration: 1500,
    minimumTimeBetweenStars: 250,
    minimumDistanceBetweenStars: 75,
    glowDuration: 180,
    glowRadius: 28,
    maximumGlowPointSpacing: 6,
    maxTeleportDistance: 250, // Distance max autorisée entre deux points avant de couper la traînée
    colors: ["249, 146, 253", "252, 254, 255"],
    sizes: [16, 12, 8],

    // Flocons de neige (base et tempête)
    baseSnowCount: 65,
    stormSnowCount: 240, // Nombre maximal de flocons pendant une tempête
    snowMinRadius: 5,
    snowMaxRadius: 15,
    snowMinSpeed: 35,
    snowMaxSpeed: 105,

    // Répulsion (souris & élément focus)
    mouseRepelRadius: 130,     // Rayon d'action autour de la souris (px)
    mouseRepelStrength: 850,   // Force d'écartement de la souris
    focusRepelPadding: 45,     // Marge de répulsion autour de l'élément focus (px)
    focusRepelStrength: 750,   // Force d'écartement de l'élément focus
    repelFriction: 0.90,       // Amortissement du mouvement d'esquive

    // Tempêtes de neige périodiques
    calmMinDuration: 14000,    // Durée min d'un temps calme (ms)
    calmMaxDuration: 28000,    // Durée max d'un temps calme (ms)
    stormMinDuration: 7000,    // Durée min d'une tempête (ms)
    stormMaxDuration: 13000,   // Durée max d'une tempête (ms)
    stormMaxWindX: 380,        // Vitesse horizontale du vent en tempête (px/s)
    stormSpeedMultiplier: 2.3  // Accélération verticale de la chute en tempête
  };

  // Utilitaires mathématiques
  const rand = (min, max) => Math.random() * (max - min) + min;
  const lerp = (a, b, t) => a + (b - a) * t;
  const selectRandom = items => items[Math.floor(Math.random() * items.length)];
  const calcDistance = (a, b) => Math.hypot(b.x - a.x, b.y - a.y);

  // 3. Pré-rendu du halo lumineux (Glow Sprite)
  const glowCanvas = document.createElement("canvas");
  const glowSize = config.glowRadius * 2;
  glowCanvas.width = glowSize * dpr;
  glowCanvas.height = glowSize * dpr;
  const glowCtx = glowCanvas.getContext("2d");
  glowCtx.scale(dpr, dpr);

  const gradient = glowCtx.createRadialGradient(
    config.glowRadius, config.glowRadius, 0,
    config.glowRadius, config.glowRadius, config.glowRadius
  );
  gradient.addColorStop(0, "rgba(249, 146, 253, 0.45)");
  gradient.addColorStop(0.4, "rgba(249, 146, 253, 0.15)");
  gradient.addColorStop(1, "rgba(249, 146, 253, 0)");

  glowCtx.fillStyle = gradient;
  glowCtx.fillRect(0, 0, glowSize, glowSize);

  // 4. Pré-rendu d'un flocon cristallin à 6 branches (Snowflake Sprite)
  const snowSpriteSize = 64;
  const snowCanvas = document.createElement("canvas");
  snowCanvas.width = snowSpriteSize * dpr;
  snowCanvas.height = snowSpriteSize * dpr;
  const snowCtx = snowCanvas.getContext("2d");
  snowCtx.scale(dpr, dpr);

  const drawSnowflakeCrystal = (c, cx, cy, r) => {
    c.save();
    c.translate(cx, cy);
    c.strokeStyle = "rgba(255, 255, 255, 0.95)";
    c.shadowColor = "rgba(255, 255, 255, 0.6)";
    c.shadowBlur = 4;
    c.lineCap = "round";
    c.lineWidth = 2;

    for (let i = 0; i < 6; i++) {
      c.rotate(Math.PI / 3);

      // Tige principale
      c.beginPath();
      c.moveTo(0, 0);
      c.lineTo(0, -r);
      c.stroke();

      // Premiers chevrons
      c.beginPath();
      c.moveTo(0, -r * 0.45);
      c.lineTo(-r * 0.28, -r * 0.7);
      c.moveTo(0, -r * 0.45);
      c.lineTo(r * 0.28, -r * 0.7);
      c.stroke();

      // Seconds chevrons
      c.beginPath();
      c.moveTo(0, -r * 0.72);
      c.lineTo(-r * 0.18, -r * 0.88);
      c.moveTo(0, -r * 0.72);
      c.lineTo(r * 0.18, -r * 0.88);
      c.stroke();
    }
    c.restore();
  };

  drawSnowflakeCrystal(snowCtx, snowSpriteSize / 2, snowSpriteSize / 2, 24);

  // 5. Pré-rendu des étoiles vectorielles (4 branches) en cache
  const drawSparkle = (c, cx, cy, outerRadius) => {
    const innerRadius = outerRadius * 0.22;
    c.beginPath();
    for (let i = 0; i < 4; i++) {
      const angle = (i * Math.PI) / 2;
      const nextAngle = ((i + 1) * Math.PI) / 2;
      const midAngle = angle + Math.PI / 4;

      const xOuter = cx + Math.cos(angle) * outerRadius;
      const yOuter = cy + Math.sin(angle) * outerRadius;
      const xInner = cx + Math.cos(midAngle) * innerRadius;
      const yInner = cy + Math.sin(midAngle) * innerRadius;

      if (i === 0) c.moveTo(xOuter, yOuter);
      c.quadraticCurveTo(xInner, yInner, cx + Math.cos(nextAngle) * outerRadius, cy + Math.sin(nextAngle) * outerRadius);
    }
    c.closePath();
    c.fill();
  };

  const starSprites = {};
  config.colors.forEach(color => {
    config.sizes.forEach(size => {
      const key = `${color}-${size}`;
      const offCanvas = document.createElement("canvas");
      const padding = 30;
      const totalSize = size * 2 + padding * 2;
      offCanvas.width = totalSize * dpr;
      offCanvas.height = totalSize * dpr;
      const offCtx = offCanvas.getContext("2d");
      offCtx.scale(dpr, dpr);

      offCtx.shadowColor = `rgba(${color}, 0.9)`;
      offCtx.shadowBlur = 16;
      offCtx.fillStyle = `rgb(${color})`;
      drawSparkle(offCtx, totalSize / 2, totalSize / 2, size);

      starSprites[key] = { canvas: offCanvas, offset: totalSize / 2 };
    });
  });

  // 6. Système météorologique (Gestion des tempêtes de neige)
  const weather = {
    isStorm: false,
    intensity: 0,           // 0 = temps calme, 1 = tempête maximale (transition fluide)
    windDirection: 1,       // 1 = vent vers la droite, -1 = vent vers la gauche
    nextChangeTime: performance.now() + rand(config.calmMinDuration, config.calmMaxDuration)
  };

  const updateWeather = (now, dt) => {
    if (now >= weather.nextChangeTime) {
      weather.isStorm = !weather.isStorm;
      if (weather.isStorm) {
        // Déclenchement d'une tempête avec direction de vent aléatoire
        weather.windDirection = Math.random() < 0.5 ? 1 : -1;
        weather.nextChangeTime = now + rand(config.stormMinDuration, config.stormMaxDuration);
      } else {
        // Retour au calme
        weather.nextChangeTime = now + rand(config.calmMinDuration, config.calmMaxDuration);
      }
    }

    // Interpolation douce de l'intensité (montée et descente progressive sur ~2.5 secondes)
    const targetIntensity = weather.isStorm ? 1 : 0;
    const transitionSpeed = 0.45 * dt;
    if (weather.intensity < targetIntensity) {
      weather.intensity = Math.min(targetIntensity, weather.intensity + transitionSpeed);
    } else if (weather.intensity > targetIntensity) {
      weather.intensity = Math.max(targetIntensity, weather.intensity - transitionSpeed);
    }
  };

  // 7. Initialisation du pool de flocons (jusqu'à stormSnowCount)
  const createSnowflake = (initialSpread = false) => {
    const radius = rand(config.snowMinRadius, config.snowMaxRadius);
    const depthRatio = (radius - config.snowMinRadius) / (config.snowMaxRadius - config.snowMinRadius);
    return {
      x: rand(0, window.innerWidth),
      y: initialSpread ? rand(-window.innerHeight, window.innerHeight) : -radius * 2,
      radius,
      depthRatio,
      baseVy: config.snowMinSpeed + depthRatio * (config.snowMaxSpeed - config.snowMinSpeed),
      // Vélocités additionnelles dues aux forces de répulsion
      repelVx: 0,
      repelVy: 0,
      rotation: rand(0, Math.PI * 2),
      vRot: rand(-0.8, 0.8),
      swayAmplitude: rand(15, 45),
      swayFrequency: rand(0.8, 2.0),
      swayOffset: rand(0, Math.PI * 2),
      opacity: 0.4 + depthRatio * 0.6
    };
  };

  const snowflakes = Array.from({ length: config.stormSnowCount }, (_, index) => {
    const flake = createSnowflake(true);
    // Seuls les flocons de base sont visibles au démarrage
    flake.active = index < config.baseSnowCount;
    return flake;
  });

  // 8. Suivi de la souris et de l'élément HTML focalisé (focus)
  const stars = [];
  const glows = [];
  const activeCursor = { x: -9999, y: -9999, isActive: false };
  const last = {
    starTimestamp: performance.now(),
    starPosition: null,
    mousePosition: null
  };

  let focusedRect = null;

  /**
   * Récupère le rectangle englobant de l'élément actuellement focus
   * (en ignorant body/html pour ne pas repousser toute la page)
   */
  const updateFocusedElementRect = () => {
    const el = document.activeElement;
    if (
      el &&
      el !== document.body &&
      el !== document.documentElement &&
      typeof el.getBoundingClientRect === "function"
    ) {
      const rect = el.getBoundingClientRect();
      // Vérifie que l'élément est visible à l'écran
      if (rect.width > 0 && rect.height > 0) {
        focusedRect = rect;
        return;
      }
    }
    focusedRect = null;
  };

  window.addEventListener("focusin", updateFocusedElementRect, { passive: true });
  window.addEventListener("focusout", () => { focusedRect = null; }, { passive: true });
  window.addEventListener("scroll", updateFocusedElementRect, { passive: true });

  const spawnStar = (x, y) => {
    const color = selectRandom(config.colors);
    const size = selectRandom(config.sizes);
    stars.push({
      x,
      y,
      vx: rand(-25, 25),
      vy: rand(60, 130),
      rotation: rand(0, Math.PI * 2),
      vRot: rand(-2.5, 2.5),
      sprite: starSprites[`${color}-${size}`],
      born: performance.now()
    });
  };

  const spawnGlow = (lastPos, currentPos) => {
    const distance = calcDistance(lastPos, currentPos);
    // Ignore l'interpolation si le curseur s'est "téléporté" (sortie/entrée d'écran)
    if (distance > config.maxTeleportDistance) return;

    const quantity = Math.max(Math.floor(distance / config.maximumGlowPointSpacing), 1);
    const dx = (currentPos.x - lastPos.x) / quantity;
    const dy = (currentPos.y - lastPos.y) / quantity;
    const now = performance.now();

    for (let i = 0; i < quantity; i++) {
      glows.push({
        x: lastPos.x + dx * i,
        y: lastPos.y + dy * i,
        born: now
      });
    }
  };

  const resetPointerTracking = () => {
    last.mousePosition = null;
    activeCursor.isActive = false;
  };

  const handleOnMove = (e, isNewStroke = false) => {
    if (!e) return;
    const pos = { x: e.clientX, y: e.clientY };

    // Mise à jour de la position de répulsion du curseur
    activeCursor.x = pos.x;
    activeCursor.y = pos.y;
    activeCursor.isActive = true;

    // Si la souris vient de rentrer dans la fenêtre, d'un nouveau touch ou d'un grand saut,
    // on réinitialise le point de départ sans tracer de segment intermédiaire
    if (
      isNewStroke ||
      !last.mousePosition ||
      calcDistance(last.mousePosition, pos) > config.maxTeleportDistance
    ) {
      last.mousePosition = { ...pos };
    }

    const now = performance.now();
    const hasMovedFarEnough =
      !last.starPosition ||
      calcDistance(last.starPosition, pos) >= config.minimumDistanceBetweenStars;
    const hasBeenLongEnough = (now - last.starTimestamp) > config.minimumTimeBetweenStars;

    if (hasMovedFarEnough || hasBeenLongEnough) {
      spawnStar(pos.x, pos.y);
      last.starTimestamp = now;
      last.starPosition = { ...pos };
    }

    spawnGlow(last.mousePosition, pos);
    last.mousePosition = { ...pos };
  };

  window.addEventListener("mousemove", e => handleOnMove(e, false), { passive: true });
  window.addEventListener("mouseenter", e => handleOnMove(e, true), { passive: true });
  window.addEventListener("touchmove", e => handleOnMove(e.touches[0], false), { passive: true });
  window.addEventListener("touchstart", e => handleOnMove(e.touches[0], true), { passive: true });
  window.addEventListener("touchend", resetPointerTracking, { passive: true });
  window.addEventListener("blur", resetPointerTracking, { passive: true });
  document.addEventListener("mouseleave", resetPointerTracking);
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) resetPointerTracking();
  });

  // 9. Boucle de rendu unique (120+ fps)
  let lastFrameTime = performance.now();

  const render = now => {
    // Plafonne dt à 0.05s pour éviter les sauts physiques si l'onglet était inactif
    const dt = Math.min((now - lastFrameTime) / 1000, 0.05);
    const elapsedSec = now / 1000;
    lastFrameTime = now;

    // Mise à jour de la météo et du rectangle de l'élément focus
    updateWeather(now, dt);
    if (document.activeElement && document.activeElement !== document.body) {
      updateFocusedElementRect();
    }

    ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);

    // Calcul des paramètres actuels selon l'intensité de la tempête
    const targetActiveCount = Math.round(
      lerp(config.baseSnowCount, config.stormSnowCount, weather.intensity)
    );
    const speedMult = lerp(1, config.stormSpeedMultiplier, weather.intensity);
    // Rafales de vent sinusoïdales pendant la tempête
    const windGust = Math.sin(elapsedSec * 2.5) * 0.25 + 0.85;
    const currentWindX =
      weather.intensity * weather.windDirection * config.stormMaxWindX * windGust;

    // --- A. Rendu et physique des flocons ---
    ctx.globalCompositeOperation = "source-over";
    const screenW = window.innerWidth;
    const screenH = window.innerHeight;

    for (let i = 0; i < snowflakes.length; i++) {
      const f = snowflakes[i];
      const shouldBeActive = i < targetActiveCount;

      if (!f.active) {
        if (shouldBeActive) {
          // Activation progressive d'un nouveau flocon de tempête depuis le haut ou les bords
          f.active = true;
          if (Math.abs(currentWindX) > 80 && Math.random() < 0.45) {
            f.x = currentWindX > 0 ? -f.radius * 2 : screenW + f.radius * 2;
            f.y = rand(0, screenH * 0.85);
          } else {
            f.x = rand(0, screenW);
            f.y = -f.radius * 2;
          }
          f.repelVx = 0;
          f.repelVy = 0;
        } else {
          continue;
        }
      }

      // 1. Mouvement naturel + vent de tempête (les gros flocons proches prennent plus le vent)
      const windFactor = 0.65 + f.depthRatio * 0.55;
      f.x += currentWindX * windFactor * dt;
      f.y += f.baseVy * speedMult * dt;

      // Rotation accélérée par le vent
      const stormSpin = weather.intensity * weather.windDirection * 2.5;
      f.rotation += (f.vRot + stormSpin) * dt;

      // Position visuelle incluant l'oscillation douce (atténuée en pleine tempête)
      const swayScale = lerp(1, 0.35, weather.intensity);
      const swayX = Math.sin(elapsedSec * f.swayFrequency + f.swayOffset) * f.swayAmplitude * swayScale;
      const visualX = f.x + swayX;
      const visualY = f.y;

      // 2. Répulsion autour de la souris / doigt
      if (activeCursor.isActive) {
        const dx = visualX - activeCursor.x;
        const dy = visualY - activeCursor.y;
        const dist = Math.hypot(dx, dy);

        if (dist < config.mouseRepelRadius && dist > 0.001) {
          const force = Math.pow(1 - dist / config.mouseRepelRadius, 1.5) * config.mouseRepelStrength;
          f.repelVx += (dx / dist) * force * dt;
          f.repelVy += (dy / dist) * force * dt;
        }
      }

      // 3. Répulsion autour de l'élément HTML actuellement focus (Boîte englobante arrondie)
      if (focusedRect) {
        const pad = config.focusRepelPadding;
        // Point le plus proche sur le rectangle de l'élément focus
        const closestX = Math.max(focusedRect.left, Math.min(visualX, focusedRect.right));
        const closestY = Math.max(focusedRect.top, Math.min(visualY, focusedRect.bottom));

        let dx = visualX - closestX;
        let dy = visualY - closestY;
        let dist = Math.hypot(dx, dy);

        // Si le flocon est strictement à l'intérieur du rectangle focus, on le pousse vers le bord le plus proche
        if (dist === 0) {
          const centerX = (focusedRect.left + focusedRect.right) * 0.5;
          const centerY = (focusedRect.top + focusedRect.bottom) * 0.5;
          dx = visualX - centerX;
          dy = visualY - centerY;
          dist = Math.hypot(dx, dy) || 1;
          f.repelVx += (dx / dist) * config.focusRepelStrength * 1.5 * dt;
          f.repelVy += (dy / dist) * config.focusRepelStrength * 1.5 * dt;
        } else if (dist < pad) {
          const force = Math.pow(1 - dist / pad, 1.4) * config.focusRepelStrength;
          f.repelVx += (dx / dist) * force * dt;
          f.repelVy += (dy / dist) * force * dt;
        }
      }

      // Application et amortissement de la vélocité de répulsion
      f.x += f.repelVx * dt;
      f.y += f.repelVy * dt;
      const damping = Math.pow(config.repelFriction, dt * 60);
      f.repelVx *= damping;
      f.repelVy *= damping;

      // 4. Réinitialisation / recyclage aux bords de l'écran
      const margin = f.radius * 3;
      const isOutBottom = f.y > screenH + margin;
      const isOutLeft = f.x < -margin * 2;
      const isOutRight = f.x > screenW + margin * 2;

      if (isOutBottom || isOutLeft || isOutRight) {
        // Si la tempête est finie et que ce flocon est en surplus, on le désactive proprement
        if (!shouldBeActive) {
          f.active = false;
          continue;
        }

        f.repelVx = 0;
        f.repelVy = 0;

        if (isOutLeft) {
          f.x = screenW + margin;
          f.y = rand(-margin, screenH);
        } else if (isOutRight) {
          f.x = -margin;
          f.y = rand(-margin, screenH);
        } else {
          // Sorti par le bas : réapparaît en haut (décalé contre le vent si tempête)
          const windOffset = currentWindX * 0.6;
          f.x = rand(Math.min(0, -windOffset), Math.max(screenW, screenW - windOffset));
          f.y = -margin;
        }
      }

      // 5. Dessin du flocon
      const drawSize = f.radius * 2.5;
      ctx.save();
      ctx.globalAlpha = f.opacity;
      ctx.translate(f.x + swayX, f.y);
      ctx.rotate(f.rotation);
      ctx.drawImage(
        snowCanvas,
        -drawSize / 2,
        -drawSize / 2,
        drawSize,
        drawSize
      );
      ctx.restore();
    }

    // --- B. Rendu de la traînée lumineuse épaisse ---
    ctx.globalCompositeOperation = "lighter";
    for (let i = glows.length - 1; i >= 0; i--) {
      const g = glows[i];
      const age = now - g.born;
      if (age >= config.glowDuration) {
        glows.splice(i, 1);
        continue;
      }
      const progress = 1 - age / config.glowDuration;
      const currentSize = glowSize * (0.4 + 0.6 * progress);
      ctx.globalAlpha = progress;

      ctx.drawImage(
        glowCanvas,
        g.x - currentSize / 2,
        g.y - currentSize / 2,
        currentSize,
        currentSize
      );
    }

    // --- C. Rendu des étoiles de la souris ---
    ctx.globalCompositeOperation = "source-over";
    for (let i = stars.length - 1; i >= 0; i--) {
      const s = stars[i];
      const age = now - s.born;
      if (age >= config.starDuration) {
        stars.splice(i, 1);
        continue;
      }

      const lifeRatio = age / config.starDuration;
      s.x += s.vx * dt;
      s.y += s.vy * dt;
      s.vy += 120 * dt;
      s.rotation += s.vRot * dt;

      ctx.save();
      ctx.globalAlpha = 1 - Math.pow(lifeRatio, 2);
      ctx.translate(s.x, s.y);
      ctx.rotate(s.rotation);
      const scale = 1 - lifeRatio * 0.4;
      ctx.scale(scale, scale);

      const { canvas: spriteCanvas, offset } = s.sprite;
      ctx.drawImage(
        spriteCanvas,
        -offset,
        -offset,
        spriteCanvas.width / dpr,
        spriteCanvas.height / dpr
      );
      ctx.restore();
    }

    ctx.globalAlpha = 1;
    requestAnimationFrame(render);
  };

  requestAnimationFrame(render);

  // 10. Conservation de votre logique ".ajd"
  let today = document.querySelector(".ajd");
  if (!today) return;
  today.classList.add("magic");
  for (let i = 0; i < 8; i++) {
    let star = document.createElement("div");
    star.className = "magic-star";
    today.appendChild(star);
  }
});
