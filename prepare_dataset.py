import os
import shutil
import random

classes = ["person", "water_bottle", "jinthaa_juice", "lifebuoy", "dhal"]

for cls in classes:
    src = os.path.join("data", "raw", cls)
    train_dst = os.path.join("data", "dataset", "images", "train")
    val_dst = os.path.join("data", "dataset", "images", "val")

    images = [
        f for f in os.listdir(src)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    random.seed(42)
    random.shuffle(images)

    split = max(1, int(len(images) * 0.8))

    for i, image in enumerate(images):
        source = os.path.join(src, image)
        prefix = cls + "_"
        destination = val_dst if i >= split else train_dst
        new_name = prefix + image
        shutil.copy2(source, os.path.join(destination, new_name))

print("Dataset split completed.")