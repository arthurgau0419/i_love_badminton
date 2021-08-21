#### Local

docker build:
```shell
  docker build badminton:latest .
```

docker run:
```shell
  docker run --rm badminton:latest crawl badminton -a account=$ORDER_ACCOUNT -a password=$ORDER_PASSWORD -a fire_date=$FIRE_DATE -a date=$ORDER_DATE -a order_time=$ORDER_TIME  -a tp=$ORDER_TP -a pt=$ORDER_PT -a pid=$ORDER_PID
```

#### Variables

* ORDER_ACCOUNT
  *運動中心帳號*

* ORDER_PASSWORD
  *運動中心密碼*

* FIRE_DATE （ORDER_DATE 前一週）

* ORDER_DATE
  `yyyy/MM/dd`

* ORDER_TIME
  `0~24`（逗號分隔）

* ORDER_TP 運動中心(e.g 內湖、大安)

* ORDER_PT 球種(e.g 羽球、桌球、壁球)

* ORDER_PID 球場 id（逗號分隔）


#### TP 對照表

|    | 中山 | 南港 | 大安 | 信義 | 文山 | 內湖 |
|----|-----|-----|------|------|-----|-----|
| TP | 01  | 02  | 03   |  04  | 06  |  12 |

|    | 蘆洲 | 土城 | 汐止 | 永和 | 林口 |
|----|-----|-----|------|------|-----|
| TP | 07  | 08  | 09   |  10  | 17  |


#### 各地 PID

內湖

|     | 羽1 | 羽2 | 羽3  | 羽4  | 羽5 | 羽6 |
|-----|-----|-----|------|------|-----|-----|
| PID | 83  | 84  | 1074 | 1075 | 87  | 88  |

大安

|     | 羽5 | 羽6 |  羽7 | 羽8  | 羽9 | 羽10 |
|-----|-----|-----|------|------|-----|-----|
| PID | 1089|1090 |1091(?)| 1092| 1093 | 1094(?)  |
