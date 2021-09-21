 #!/bin/sh
echo 'generating FluidSynth system banks'
python3 sf2banks.py autoload.rg 1.rg '/zynthian/zynthian-data/soundfonts/sf2/' 0 FluidSynth

echo 'generating FluidSynth user banks'
python3 sf2banks.py 1.rg 2.rg '/zynthian/zynthian-my-data/soundfonts/sf2/' 1 FluidSynth

echo 'generating ZynAddSubFX banks'
python3 zyn2banks.py 2.rg generated.rg '/zynthian/zynthian-data/' 0 ZynAddSubFx





