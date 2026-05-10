
import pandas as pd
from pathlib import Path
ROOT = Path(__file__).parent.parent

def plot_3D(df, z_col):
    import plotly.express as px
    from pathlib import Path
    
    df[z_col] = df['risk'].apply(lambda risk: risk.get(z_col))

    x_col = "multiplier_soler" if "multiplier_soler" in df.columns else "multiplier_solar"
    y_col= "multiplier_wind"   

    fig = px.scatter_3d(
        df,
        x=x_col,
        y= y_col,
        z=df['risk'].apply(lambda risk: risk.get(z_col)),
        color=z_col,
        color_continuous_scale="Viridis",
        labels={
            x_col: "Solar Multiplier",
            "multiplier_wind": "Wind Multiplier",
            z_col: f"{z_col} (MW)",
        },
        title=f"3D Sensitivity: {z_col} vs Solar/Wind Multipliers",
        hover_data={x_col: True, "multiplier_wind": True, z_col: ":.2f"},
    )

    fig.update_traces(marker=dict(size=4, opacity=0.85))
    fig.update_layout(
        coloraxis_colorbar=dict(title=f"{z_col} (MW)"),
        margin=dict(l=0, r=0, b=0, t=40),
        width=850,
        height=650,
    )
    fig.show()
    
    # Save as static image for GitHub
    figures_dir = ROOT / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    
    img_path = figures_dir / f"3d_{z_col}.png"
    html_path = figures_dir / f"3d_{z_col}.html"
    
    fig.write_image(str(img_path), width=850, height=650)
    fig.write_html(str(html_path))
    
    print(f"Saved: {img_path.relative_to(ROOT)}")
    print(f"Saved: {html_path.relative_to(ROOT)}")
    
    return fig