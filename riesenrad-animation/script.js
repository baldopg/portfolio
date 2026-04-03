document.addEventListener("DOMContentLoaded", () => {
  // 1. Generate Stars (only if #stars container exists — not used in portfolio)
  const container = document.getElementById("stars");
  if (container) {
    const starCount = 50;
    for (let i = 0; i < starCount; i++) {
      const star = document.createElement("div");
      star.className = "star";
      const x = Math.random() * 100;
      const y = Math.random() * 100;
      const size = Math.random() * 1 + 1;
      star.style.left = `${x}vw`;
      star.style.top = `${y}vh`;
      star.style.width = `${size}px`;
      star.style.height = `${size}px`;
      container.appendChild(star);
    }
  }

  // 2. Loop Wheel Animation via requestAnimationFrame
  const TOTAL_DURATION_MS = 40000; // 40 seconds per full rotation
  const wheelTarget = document.getElementById("wheel-technical");
  
  // Pivot points based on SVG coords
  const CX = 400;
  const CY = 340;

  // Gather all cabins so we can individually counter-rotate them
  const cabinGroups = document.querySelectorAll('.cabin-group');
  const cabinCounters = [];
  
  cabinGroups.forEach(group => {
    // Read the static initial angle for this cabin piece
    const baseAngle = parseFloat(group.getAttribute('data-angle'));
    const counterGroup = group.querySelector('.cabin-counter');
    cabinCounters.push({
      element: counterGroup,
      baseAngle: baseAngle
    });
  });

  let startTime = null;

  function animate(timestamp) {
    if (!startTime) startTime = timestamp;
    const runtime = timestamp - startTime;
    
    // Continuous rotation
    const progress = (runtime % TOTAL_DURATION_MS) / TOTAL_DURATION_MS;
    const currentAngle = progress * 360; 
    
    // Rotate entire wheel clockwise around 400,340
    wheelTarget.setAttribute("transform", `rotate(${currentAngle} ${CX} ${CY})`);
    
    // Make cabins remain visually horizontal
    cabinCounters.forEach(cabin => {
      // The parent transforms naturally pass rotation. 
      // The total rotation of a cabin = currentAngle + baseAngle.
      // So to negate it and remain horizontal -> - (currentAngle + baseAngle)
      const counterAngle = -(currentAngle + cabin.baseAngle);
      // We apply standard transform to cancel it out around structure's local translation pivot
      // Pivot is exactly where the rect anchors inside its translate.
      cabin.element.setAttribute("transform", `translate(400 50) rotate(${counterAngle}) translate(-19 -10)`);
    });

    requestAnimationFrame(animate);
  }

  requestAnimationFrame(animate);
});
