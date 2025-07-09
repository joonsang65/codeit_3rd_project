OmniGen2 설정은 다음과 같습니다:

# 깃허브 레포 클론.
git clone git@github.com:VectorSpaceLab/OmniGen2.git
cd OmniGen2

# 2. 파이쏜 가상 환경.
conda create -n omnigen2 python=3.11
conda activate omnigen2

# 의존성 설치.
pip install torch==2.6.0 torchvision --extra-index-url https://download.pytorch.org/whl/cu124
pip install -r requirements.txt
pip install flash-attn==2.7.4.post1 --no-build-isolation
