# Validation results

Positive = clay > 0.25 and clay in the top-2 minerals; target = `clay_prior > 0.55`; scored on valid survey pixels.

| scenario | recall | precision | F1 | clay mean |
|---|---:|---:|---:|---:|
| normal | 0.8575 | 0.3511 | 0.4982 | 0.1739 |
| leave-out ch0,1 | 0.8678 | 0.2347 | 0.3695 | 0.3331 |
| leave-out ch2,3 | 0.7774 | 0.2812 | 0.4130 | 0.1961 |
| leave-out ch4,5 | 0.9062 | 0.3289 | 0.4826 | 0.1983 |
| leave-out ch6,7 | 0.8199 | 0.4161 | 0.5521 | 0.1448 |
| leave-out ch8,9 | 0.7487 | 0.4742 | 0.5806 | 0.1273 |
| emi degraded x5 | 0.4937 | 0.6385 | 0.5569 | 0.0945 |
| emi failed x20 | 0.3376 | 0.7017 | 0.4559 | 0.0799 |
| tir degraded x5 | 0.9494 | 0.2987 | 0.4544 | 0.2632 |
| gamma degraded x5 | 0.8602 | 0.2546 | 0.3929 | 0.2662 |
| emi+tir failed | 0.9523 | 0.4209 | 0.5838 | 0.2100 |
| T= -60C | 0.9569 | 0.2670 | 0.4175 | 0.3589 |
| T= -40C | 0.9489 | 0.2841 | 0.4373 | 0.2871 |
| T= -25C | 0.9228 | 0.3154 | 0.4701 | 0.2173 |
| T=   0C | 0.8846 | 0.3401 | 0.4913 | 0.1855 |
| T=  25C | 0.8574 | 0.3430 | 0.4900 | 0.1780 |
| T=  50C | 0.8841 | 0.3265 | 0.4769 | 0.1946 |
| T=  70C | 0.9261 | 0.2901 | 0.4419 | 0.2519 |
| T=  80C | 0.9177 | 0.2811 | 0.4303 | 0.2603 |
| target: direct transfer | 0.8584 | 0.3513 | 0.4985 | 0.1741 |
| target: CORAL | 0.7994 | 0.3344 | 0.4715 | 0.1722 |
| H +/-0% | 0.8575 | nan | nan | nan |
| H +/-5% | 0.8599 | nan | nan | nan |
| H +/-10% | 0.8620 | nan | nan | nan |
| H +/-15% | 0.8633 | nan | nan | nan |
| H +/-20% | 0.8636 | nan | nan | nan |
| H +/-30% | 0.8591 | nan | nan | nan |

## Family means

| family | recall |
|---|---:|
| normal | 0.8575 |
| leave_channels_out | 0.8240 |
| sensor_degradation | 0.7187 |
| temperature | 0.9123 |
| cross_domain_coral | 0.7994 |
| H_sensitivity | 0.8609 |
| **overall (mean proxy recall)** | **0.8288** |
