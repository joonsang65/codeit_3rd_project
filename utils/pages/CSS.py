app_sidebar_CSS ={
            "container": {"padding": "10px"},
            "icon": {"color": "#4A8CF1", "font-size": "20px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "--hover-color": "#e6f0ff",
                "border-radius": "8px",
            },
            "nav-link-selected": {
                "background-color": "#4A8CF1",
                "color": "white",
                "font-weight": "bold",
                "border-radius": "8px",
            },
            "menu-title": {"font-size": "22px", "font-weight": "bold"},
        }

home_card_CSS = f"""
            <style>
                .clickable-card {{
                    border: 1px solid #ddd;
                    border-radius: 12px;
                    padding: 16px;
                    text-align: center;
                    box-shadow: 2px 2px 12px rgba(0,0,0,0.05);
                    margin-bottom: 20px;
                    transition: transform 0.2s ease-in-out;
                    cursor: pointer;
                }}
                .clickable-card:hover {{
                    transform: scale(1.02);
                    box-shadow: 4px 4px 20px rgba(0,0,0,0.1);
                }}
                .clickable-card img {{
                    max-width: 100%;
                    height: auto;
                    object-fit: contain;
                    border-radius: 8px;
                    margin-bottom: 8px;
                }}
                .clickable-card h4 {{
                    margin-bottom: 12px;
                    color: #222;
                }}
                .clickable-card p {{
                    color: #555;
                    font-size: 14px;
                }}
            </style>
            """

def gallery_base_CSS(animation_name, duration): 
    return f"""
    <style>
    .slider {{
        white-space: nowrap;
        overflow: hidden;
        position: relative;
        background-color: #f9f9f9;
        padding: 10px 0;
        margin-bottom: 20px;
        border-radius: 12px;
    }}
    .slide-track {{
        display: inline-block;
        animation: {animation_name} {duration}s linear infinite;
    }}
    .slide-track img {{
        height: 150px;
        margin: 0 15px;
        display: inline-block;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}
    @keyframes scroll-left {{
        0%   {{ transform: translateX(0); }}
        100% {{ transform: translateX(-50%); }}
    }}
    @keyframes scroll-right {{
        0%   {{ transform: translateX(0); }}
        100% {{ transform: translateX(50%); }}
    }}
    </style>
    """

sub1_CSS = """
        <style>
        .container-box {
            background-color: #F4F6FA;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin-bottom: 20px;
            min-height: 500px;
        }
        .stSlider label { color: #262730 !important; }
        .stSlider > div > div > div > div > div > div { color: #262730 !important; }
        </style>
        """

sub2_CSS = """
        <style>
        .box-style {
            background-color: #f9f9f9;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 0 8px rgba(0, 0, 0, 0.05);
            height: 100%;
        }
        .center-button {
            display: flex;
            justify-content: center;
            margin-top: 10px;
        }
        .full-height-textarea textarea {
            min-height: 330px !important;
        }
        </style>
        """

sub3_CSS = """
        <style>
        .box-style {
            background-color: #f9f9f9;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 0 8px rgba(0, 0, 0, 0.05);
            height: 100%;
        }
        .center-button {
            display: flex;
            justify-content: center;
            margin-top: 10px;
        }
        .full-height-textarea textarea {
            min-height: 330px !important;
        }
        </style>
        """