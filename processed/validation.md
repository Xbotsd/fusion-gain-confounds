# Validation results

Positive = clay > 0.25 and clay in the top-2 minerals; target = `clay_prior > 0.55`; scored on valid survey pixels.

| scenario | recall | precision | F1 | clay mean |
|---|---:|---:|---:|---:|
| normal | 0.6933 | 0.1654 | 0.2671 | 0.4583 |
| leave-out ch0,1 | 0.5272 | 0.0952 | 0.1613 | 0.5735 |
| leave-out ch2,3 | 0.6988 | 0.1731 | 0.2775 | 0.4369 |
| leave-out ch4,5 | 0.5524 | 0.1515 | 0.2378 | 0.4052 |
| leave-out ch6,7 | 0.6576 | 0.1592 | 0.2563 | 0.4761 |
| leave-out ch8,9 | 0.9581 | 0.2001 | 0.3311 | 0.5914 |
| emi degraded x5 | 0.9521 | 0.1990 | 0.3292 | 0.5467 |
| emi failed x20 | 0.9759 | 0.2015 | 0.3340 | 0.5589 |
| tir degraded x5 | 0.4328 | 0.1336 | 0.2041 | 0.3646 |
| gamma degraded x5 | 0.6019 | 0.1086 | 0.1840 | 0.5525 |
| emi+tir failed | 0.7695 | 0.2010 | 0.3187 | 0.4676 |
| T= -60C | 0.3519 | 0.1164 | 0.1750 | 0.3357 |
| T= -40C | 0.3876 | 0.1237 | 0.1875 | 0.3494 |
| T= -25C | 0.4771 | 0.1390 | 0.2153 | 0.3805 |
| T=   0C | 0.6029 | 0.1566 | 0.2487 | 0.4241 |
| T=  25C | 0.6897 | 0.1631 | 0.2638 | 0.4594 |
| T=  50C | 0.5703 | 0.1496 | 0.2370 | 0.4156 |
| T=  70C | 0.3817 | 0.1182 | 0.1805 | 0.3484 |
| T=  80C | 0.3483 | 0.1094 | 0.1665 | 0.3357 |
| target: direct transfer | 0.6915 | 0.1651 | 0.2666 | 0.4562 |
| target: CORAL | 0.6894 | 0.1652 | 0.2665 | 0.4509 |
| H +/-0% | 0.6933 | nan | nan | nan |
| H +/-5% | 0.7012 | nan | nan | nan |
| H +/-10% | 0.6982 | nan | nan | nan |
| H +/-15% | 0.6886 | nan | nan | nan |
| H +/-20% | 0.6785 | nan | nan | nan |
| H +/-30% | 0.6594 | nan | nan | nan |

## Family means

| family | recall |
|---|---:|
| normal | 0.6933 |
| leave_channels_out | 0.6788 |
| sensor_degradation | 0.7464 |
| temperature | 0.4762 |
| cross_domain_coral | 0.6894 |
| H_sensitivity | 0.6865 |
| **overall (mean proxy recall)** | **0.6618** |
