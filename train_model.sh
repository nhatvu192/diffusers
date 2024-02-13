export MODEL_NAME="CompVis/stable-diffusion-v1-4"
export DATASET_NAME="../kanji_dataset"

accelerate launch --mixed_precision="fp16"  examples/text_to_image/train_text_to_image.py \
  --pretrained_model_name_or_path=$MODEL_NAME \
  --train_data_dir=$DATASET_NAME \
  --use_ema \
  --resolution=128 \
  --train_batch_size=16 \
  --gradient_accumulation_steps=4 \
  --gradient_checkpointing \
  --max_train_steps=4000 \
  --learning_rate=1e-05 \
  --max_grad_norm=1 \
  --lr_scheduler="constant" --lr_warmup_steps=0 \
  --output_dir="../kanji_weight2" \
  --checkpointing_steps=2000