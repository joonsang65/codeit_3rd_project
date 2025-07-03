from modules.config_loader import load_config
from modules.gpt_module import GPTClient
from modules.lora_manager import load_pipe_with_loras
from modules.ad_generator import generate_ad_banner

def main():
    config = load_config()
    gpt_client = GPTClient(
        api_key=os.getenv(config["openai"]["api_key_env"]),
        model_name=config["openai"]["gpt_model"]
    )
    pipe = load_pipe_with_loras(config, "food")

    generate_ad_banner(config, gpt_client, pipe)

if __name__ == "__main__":
    import os
    main()
