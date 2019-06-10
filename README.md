# the-third-eye-py

## Pre-install

- [YOLO3-4-Py](https://github.com/madhawav/YOLO3-4-Py)
- [SORT](https://github.com/abewley/sort)
- [FastDTW](https://github.com/slaypni/fastdtw)


### SORT requirements

```
sudo pip3 install scipy \
filterpy \
numba \
scikit-image \
scikit-learn \
cffi
```

#### Issue

- [MNT Import linear assignment from scipy #13465](https://github.com/scikit-learn/scikit-learn/pull/13465)
    - [Files changed #13465](https://github.com/scikit-learn/scikit-learn/pull/13465/files/d33177f2ed64a6bf5cb8b10deec13b7adff48c97#diff-160ed32d41d06a19cbc9fb51c4e4fd2a)

### FastDTW 

```
sudo pip3 install fastdtw
```

## Config

- Yolo Server Port `8091`
- Display Server Port `8092`
- Stream Server Port `8090`
- Check Box Port `8099`
    - URL `/fusion/<int:room_id>`

## Run

- Command (Selector)

```
python3 checkbox_web.py
```

- Stream Server

```
python3 mjpeg_streamer.py
```

- Display Server

```
python3 yolo_display.py
```

- Yolo Server

```
python3 yolo_server.py
```

- Location

```
python3 DAI_push_location.py
```

- Yolo Client

```
python3 yolo_detector.py
```

### All Command

```
python3 checkbox_web.py
python3 mjpeg_streamer.py
python3 yolo_display.py
python3 yolo_server.py
python3 DAI_push_location.py
python3 yolo_detector.py
```

### Flow

`Yolo Client` -> `Yolo Server` -> `Display Server` -> `Stream Server`

