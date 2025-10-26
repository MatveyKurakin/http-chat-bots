import cv2
import numpy as np


def data_to_img(data):
    nparr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    assert not img is None
    return img


def img_to_data(img):
    success, enc_img = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 85])
    assert success
    return enc_img.tobytes()


def grayscale(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def sepia(img):
    sepia_filter = np.array(
        [[0.393, 0.769, 0.189], [0.349, 0.686, 0.168], [0.272, 0.534, 0.131]]
    )
    return cv2.transform(img, sepia_filter)


def invert(img):
    return cv2.bitwise_not(img)


def posterize(img, levels=4):
    return (img // (256 // levels)) * (256 // levels)


def gaussian(img, **params):
    kernel_sizes = [1, 5, 11, 19, 29, 41]
    kernel_size = kernel_sizes[params["intensity"] // 20]
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)


def median(img, **params):
    kernel_sizes = [1, 5, 11, 19, 29, 41]
    kernel_size = kernel_sizes[params["intensity"] // 20]
    return cv2.medianBlur(img, kernel_size)


def sharpen(img, **params):
    strength_sizes = [0.0, 0.3, 0.6, 1.2, 1.5, 1.8, 2.1, 2.4, 2.7, 3.0]
    strength = strength_sizes[params["intensity"] // 20]
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]) * strength
    return cv2.filter2D(img, -1, kernel)


def brightness(img, **params):
    brightness_values = [0, 51, 102, 153, 204, 255]
    param = params["intensity"]
    if param < 0:
        brightness = brightness_values[param // -20]
    else:
        brightness = -brightness_values[param // 20]
    return cv2.convertScaleAbs(img, alpha=1.0, beta=brightness)


def saturation(img, **params):
    saturation_values = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]
    saturation = saturation_values[params["intensity"] // 20]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * saturation, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


def color_balance(img, **params):
    img_float = img.astype(np.float32)
    scale_values = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]
    blue = params.get("blue_intensity", 0)
    green = params.get("green_intensity", 0)
    red = params.get("red_intensity", 0)

    blue_scale = scale_values[blue // 20]
    green_scale = scale_values[green // 20]
    red_scale = scale_values[red // 20]

    b, g, r = cv2.split(img_float)
    b = np.clip(b * blue_scale, 0, 255)
    g = np.clip(g * green_scale, 0, 255)
    r = np.clip(r * red_scale, 0, 255)

    result = cv2.merge([b, g, r])
    return result.astype(np.uint8)


def vignette(img, **params):
    strength_sizes = [0.0, 0.4, 0.8, 1.2, 1.6, 2.0]
    strength = strength_sizes[params["intensity"] // 20]
    rows, cols = img.shape[:2]
    kernel_x = cv2.getGaussianKernel(cols, cols / 3)
    kernel_y = cv2.getGaussianKernel(rows, rows / 3)
    kernel = kernel_y * kernel_x.T
    mask = kernel / kernel.max()
    return (img * mask[:, :, np.newaxis] * strength).astype(np.uint8)


def add_noise(img, **params):
    intensity_sizes = [0, 6, 12, 18, 24, 30]
    intensity = intensity_sizes[params["intensity"] // 20]
    noise = np.random.randint(-intensity, intensity, img.shape)
    noisy = img + noise
    return np.clip(noisy, 0, 255).astype(np.uint8)


def pixel_art(img, **params):
    intensity_sizes = [2, 8, 14, 20, 26, 3]
    h, w = img.shape[:2]
    max_size = min(h, w) // 4
    pixel_size = max(2, min(max_size, intensity_sizes[params["intensity"] // 20]))

    small = cv2.resize(
        img, (w // pixel_size, h // pixel_size), interpolation=cv2.INTER_NEAREST
    )
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)


def fisheye(img, **params):
    strength_sizes = [0.0, 0.2, 0.35, 0.45, 0.5]
    param = params["intensity"]
    if param < 0:
        strength = -strength_sizes[param // -20]
    else:
        strength = strength_sizes[param // 20]

    h, w = img.shape[:2]
    map_x, map_y = np.zeros((h, w), np.float32), np.zeros((h, w), np.float32)

    for i in range(h):
        for j in range(w):
            x = (2 * j - w) / w
            y = (2 * i - h) / h
            r = np.sqrt(x * x + y * y)
            theta = np.arctan2(y, x)

            r = r * (1 - strength * r * r)

            map_x[i, j] = (r * np.cos(theta) + 1) * w / 2
            map_y[i, j] = (r * np.sin(theta) + 1) * h / 2

    return cv2.remap(img, map_x, map_y, cv2.INTER_LINEAR)
