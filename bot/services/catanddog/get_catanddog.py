from random import choice

cat_urls: list[str] = [
    "https://png.pngtree.com/png-vector/20241012/ourlarge/pngtree-cat-peeking-from-frame-png-image_14067902.png",
    "https://png.pngtree.com/png-clipart/20250421/original/pngtree-shorthaired-cat-pet-animal-png-image_20753774.png",
    "https://png.pngtree.com/png-clipart/20240826/original/pngtree-portrait-of-a-cute-confused-tabby-cat-on-transparent-background-png-image_15854005.png",
    "https://png.pngtree.com/png-clipart/20250501/original/pngtree-cat-jumping-for-free-download-png-image_20917199.png",
]

dog_urls: list[str] = [
    "https://png.pngtree.com/png-clipart/20230514/original/pngtree-smile-dog-on-white-background-png-image_9160783.png",
    "https://png.pngtree.com/png-clipart/20240614/original/pngtree-friendly-dog-png-image_15323818.png",
    "https://png.pngtree.com/png-clipart/20230409/original/pngtree-dog-cute-animal-realistic-png-image_9040414.png",
]


async def get_cat() -> str:
    return choice(cat_urls)


async def get_dog() -> str:
    return choice(dog_urls)
