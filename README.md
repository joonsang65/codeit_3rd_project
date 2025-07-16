# 이미지 생성 모듈화 (진행 중)

model_dev 폴더 내부의 image_module.py를 임포트 하여 확인 하실 수 있습니다.

## 실행 분기
step1(): 이미지의 전처리 과정을 실행합니다. (배경 생성의 경우 불필요 합니다.)
step2(): mode 설정을 하여 text2img 혹은 inpaint 과정을 수행하게 됩니다.
    - text2img (배경 생성)의 경우 mode만 입력하면 되며 나머지 인자는 무시하게 됩니다.
    - inpaint 모드의 경우 step1()에서 생성된 canvas와 mask 인자를 넘겨 주어야만 합니다.

## 응용 방법:
```<code>
import os
import sys
print(sys.path) # 여기에 '..../model_dev' 경로가 포함되어 있다면 경로의 문제가 없습니다.

# 아니라면 경로를 추적해 봅시다. 올바른 경로를 찾아 시스템 경로에 추가해 줍시다.
print(os.path.abspath('./'))
print(os.path.dirname(os.path.abspath('./')))
# sys.path.append()

import image_module # 모듈 초기화가 내부적으로 진행됩니다.
print(image_module.cfg) # 내부적인 설정을 확인합니다.

# 실행합니다. 배경생성의 경우 'inpaint' -> 'text2img'
canvas, back_rm_canv, mask = image_module.step1()
top_image = image_module.step2('inpaint', canvas, mask)
```