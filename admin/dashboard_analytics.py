"""
dashboard_analytics.py - Dashboard visual IA vs Reglas

Panel de administración para ver métricas en tiempo real.
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/admin/analytics", tags=["analytics"])

@router.get("/", response_class=HTMLResponse)
async def dashboard_analytics():
    """Dashboard principal de Analytics IA vs Reglas"""
    
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📊 Dashboard Analytics - BotlyPro</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #f5f7fa;
                color: #333;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            .header h1 { font-size: 28px; margin-bottom: 10px; }
            .header p { opacity: 0.9; }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 30px;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .card {
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            }
            .card h3 {
                color: #718096;
                font-size: 14px;
                text-transform: uppercase;
                margin-bottom: 10px;
            }
            .metric {
                font-size: 36px;
                font-weight: bold;
                color: #667eea;
            }
            .metric.small { font-size: 24px; }
            .refresh-btn {
                background: #667eea;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                margin-bottom: 20px;
            }
            .refresh-btn:hover { background: #5568d3; }
            .table-container {
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.08);
                overflow-x: auto;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th {
                background: #667eea;
                color: white;
                padding: 12px;
                text-align: left;
                font-size: 12px;
                text-transform: uppercase;
            }
            td {
                padding: 12px;
                border-bottom: 1px solid #e2e8f0;
                font-size: 14px;
            }
            tr:hover { background: #f7fafc; }
            .badge {
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
            }
            .badge-ia { background: #c6f6d5; color: #22543d; }
            .badge-reglas { background: #feebc8; color: #744210; }
            .loading { text-align: center; padding: 40px; color: #718096; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Dashboard Analytics</h1>
            <p>IA vs Reglas - Métricas en tiempo real</p>
        </div>
        
        <div class="container">
            <button class="refresh-btn" onclick="cargarDatos()">🔄 Actualizar Datos</button>
            
            <div id="loading" class="loading">Cargando métricas...</div>
            
            <div id="dashboard" style="display:none;">
                <div class="grid">
                    <div class="card">
                        <h3>🤖 Decisiones con IA</h3>
                        <div class="metric" id="metric-ia">-</div>
                    </div>
                    
                    <div class="card">
                        <h3>⚙️ Decisiones solo Reglas</h3>
                        <div class="metric" id="metric-reglas">-</div>
                    </div>
                    
                    <div class="card">
                        <h3>🧠 Precisión Estimada</h3>
                        <div class="metric" id="metric-precision">-%</div>
                    </div>
                    
                    <div class="card">
                        <h3>💬 Total Decisiones</h3>
                        <div class="metric" id="metric-total">-</div>
                    </div>
                </div>
                
                <div class="table-container">
                    <h3 style="margin-bottom:15px;">📋 Últimas Decisiones</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Hora</th>
                                <th>Usuario</th>
                                <th>Mensaje</th>
                                <th>Reglas</th>
                                <th>IA</th>
                            </tr>
                        </thead>
                        <tbody id="tabla-decisiones">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <script>
            async function cargarDatos() {
                document.getElementById('loading').style.display = 'block';
                document.getElementById('dashboard').style.display = 'none';
                
                try {
                    // Cargar resumen
                    const resumenRes = await fetch('/api/dashboard/resumen');
                    const resumen = await resumenRes.json();
                    
                    document.getElementById('metric-ia').textContent = resumen.ia_vs_reglas.ia;
                    document.getElementById('metric-reglas').textContent = resumen.ia_vs_reglas.reglas;
                    document.getElementById('metric-total').textContent = resumen.total_decisiones;
                    
                    // Cargar métricas IA
                    const iaRes = await fetch('/api/dashboard/ia');
                    const ia = await iaRes.json();
                    document.getElementById('metric-precision').textContent = ia.precision_estimada + '%';
                    
                    // Cargar decisiones
                    const decisionesRes = await fetch('/api/dashboard/decisiones?limit=20');
                    const decisiones = await decisionesRes.json();
                    
                    const tbody = document.getElementById('tabla-decisiones');
                    tbody.innerHTML = '';
                    
                    decisiones.decisiones.forEach(d => {
                        const row = document.createElement('tr');
                        const hora = d.created_at ? d.created_at.substring(11, 16) : '-';
                        const iaBadge = d.decision_ia 
                            ? `<span class="badge badge-ia">${d.decision_ia}</span>` 
                            : '<span style="color:#a0aec0;">-</span>';
                        
                        row.innerHTML = `
                            <td>${hora}</td>
                            <td>${d.usuario_id?.substring(0, 15) || '-'}...</td>
                            <td>${d.mensaje?.substring(0, 40) || '-'}...</td>
                            <td><span class="badge badge-reglas">${d.decision_reglas || '-'}</span></td>
                            <td>${iaBadge}</td>
                        `;
                        tbody.appendChild(row);
                    });
                    
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('dashboard').style.display = 'block';
                    
                } catch (error) {
                    document.getElementById('loading').textContent = 'Error cargando datos: ' + error.message;
                }
            }
            
            // Cargar al iniciar
            cargarDatos();
        </script>
    </body>
    </html>
    """
    return html_content
