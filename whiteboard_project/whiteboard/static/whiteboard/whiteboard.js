document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('whiteboard-canvas');
    const ctx = canvas.getContext('2d');
    let isDrawing = false;
    let lastX = 0;
    let lastY = 0;
    let currentColor = '#000000';
    let brushSize = 5;
    let isEraser = false;
    const strokeHistory = [];
    let currentStroke = [];

    
    function resizeCanvas() {
        canvas.width = window.innerWidth * 0.95;
        canvas.height = window.innerHeight * 0.85;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    function redrawCanvas() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        strokeHistory.forEach(stroke => {
            if (stroke.points.length < 2) return;
            
            ctx.strokeStyle = stroke.color;
            ctx.lineWidth = stroke.size;
            ctx.globalCompositeOperation = stroke.isEraser ? 'destination-out' : 'source-over';
            
            ctx.beginPath();
            ctx.moveTo(stroke.points[0][0], stroke.points[0][1]);
            
            for (let i = 1; i < stroke.points.length; i++) {
                ctx.lineTo(stroke.points[i][0], stroke.points[i][1]);
            }
            ctx.stroke();
        });
        ctx.globalCompositeOperation = 'source-over';
    }

    
    function startDrawing(e) {
        isDrawing = true;
        [lastX, lastY] = getPosition(e);
        currentStroke = {
            points: [[lastX, lastY]],
            color: isEraser ? '#FFFFFF' : currentColor,
            size: brushSize,
            isEraser: isEraser
        };
    }

    function draw(e) {
    if (!isDrawing) return;
    
    const [x, y] = getPosition(e);
    
    ctx.strokeStyle = isEraser ? '#FFFFFF' : currentColor;
    ctx.lineWidth = brushSize;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.globalCompositeOperation = isEraser ? 'destination-out' : 'source-over';
    
    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(x, y);
    ctx.stroke();
    
    currentStroke.points.push([x, y]); 
    lastX = x;
    lastY = y;
}

function stopDrawing() {
    if (isDrawing && currentStroke.points.length > 1) {
        strokeHistory.push(currentStroke);
    }
    isDrawing = false;
}

     function undoLastStroke() {
        if (strokeHistory.length > 0) {
            strokeHistory.pop();
            redrawCanvas();
        }
    }
    
    function getPosition(e) {
        let x, y;
        
        if (e.type.includes('touch')) {
            const touch = e.touches[0] || e.changedTouches[0];
            const rect = canvas.getBoundingClientRect();
            x = touch.clientX - rect.left;
            y = touch.clientY - rect.top;
        } else {
            const rect = canvas.getBoundingClientRect();
            x = e.clientX - rect.left;
            y = e.clientY - rect.top;
        }
        
        return [x, y];
    }

    
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseout', stopDrawing);

    
    canvas.addEventListener('touchstart', (e) => {
        e.preventDefault();
        startDrawing(e);
    });

    canvas.addEventListener('touchmove', (e) => {
        e.preventDefault();
        draw(e);
    });

    canvas.addEventListener('touchend', stopDrawing);

   
    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.addEventListener('touchstart', (e) => e.preventDefault());
    });
    
    document.querySelectorAll('.color-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            currentColor = btn.dataset.color;
            
            document.querySelectorAll('.color-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });

    
    document.querySelectorAll('.brush-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            brushSize = parseInt(btn.dataset.size);
            
            document.querySelectorAll('.brush-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });

    document.getElementById('undo-btn').addEventListener('click', undoLastStroke);
    
    document.getElementById('clear-btn').addEventListener('click', () => {
    if (confirm('Are you sure you want to clear the whiteboard?')) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        strokeHistory.length = 0; 
    }
});

    
    document.getElementById('save-btn').addEventListener('click', () => {
        const link = document.createElement('a');
        link.download = 'whiteboard.png';
        link.href = canvas.toDataURL('image/png');
        link.click();
    });

   document.getElementById('eraser-btn').addEventListener('click', function() {
    isEraser = !isEraser;
    this.classList.toggle('active');
    canvas.style.cursor = isEraser ? "not-allowed" : "crosshair";
    
    
    canvas.style.boxShadow = isEraser 
        ? '0 0 10px rgba(255,0,0,0.3)' 
        : 'none';
    setTimeout(() => canvas.style.boxShadow = 'none', 500);
});
});
