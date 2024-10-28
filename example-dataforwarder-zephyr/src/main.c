// #include <zephyr.h>
// #include <sys/printk.h>
// #include <drivers/sensor.h>
// #include <stdio.h>
// #include <stdlib.h>

// static int64_t sampling_freq = 104; // in Hz.
// static int64_t time_between_samples_us = (1000000 / (sampling_freq - 1));

// int main() {
//     // output immediately without buffering
//     setvbuf(stdout, NULL, _IONBF, 0);

//     // get driver for the accelerometer
//     const struct device *lis2dh12 =  DEVICE_DT_GET_ANY(st_lis2dh);
//     if (lis2dh12 == NULL) {
//         printf("Could not get IIS2DLPC device\n");
//         return 1;
//     }

//     struct sensor_value accel[3];

//     while (1) {
//         // start a timer that expires when we need to grab the next value
//         struct k_timer next_val_timer;
//         k_timer_init(&next_val_timer, NULL, NULL);
//         k_timer_start(&next_val_timer, K_USEC(time_between_samples_us), K_NO_WAIT);

//         // read data from the sensor
//         if (sensor_sample_fetch(lis2dh12) < 0) {
//             printf("IIS2DLPC Sensor sample update error\n");
//             return 1;
//         }

//         sensor_channel_get(lis2dh12, SENSOR_CHAN_ACCEL_XYZ, accel);

//         // print over stdout
//         printf("%.3f\t%.3f\t%.3f\r\n",
//             sensor_value_to_double(&accel[0]),
//             sensor_value_to_double(&accel[1]),
//             sensor_value_to_double(&accel[2]));

//         // busy loop until next value should be grabbed
//         while (k_timer_status_get(&next_val_timer) <= 0);
//     }
// }

#include <zephyr.h>
#include <sys/printk.h>
#include <drivers/sensor.h>
#include <drivers/gpio.h>
#include <stdio.h>
#include <stdlib.h>

/* 1000 msec = 1 sec */
#define SLEEP_TIME_MS   1000

/* The devicetree node identifier for the "led0" alias. */
#define LED0_NODE DT_ALIAS(led0)

/*
 * A build error on this line means your board is unsupported.
 * See the sample documentation for information on how to fix this.
 */
static const struct gpio_dt_spec led = GPIO_DT_SPEC_GET(LED0_NODE, gpios);

static int64_t sampling_freq = 104; // in Hz.

int main() {
    // output immediately without buffering
    setvbuf(stdout, NULL, _IONBF, 0);

    // Calculate time between samples
    int64_t time_between_samples_us = (1000000 / (sampling_freq - 1));

    // get driver for the accelerometer
    const struct device *lis2dh12 =  DEVICE_DT_GET_ANY(st_lis2dh);
    if (lis2dh12 == NULL) {
        printk("Could not get IIS2DLPC device\n");
        return 1;
    }

    // Initialize the GPIO device for the LED
    if (!device_is_ready(led.port)) {
        printk("LED device not ready\n");
        return 1;
    }

    int ret = gpio_pin_configure_dt(&led, GPIO_OUTPUT_ACTIVE);
    if (ret < 0) {
        printk("Could not configure LED pin\n");
        return 1;
    }

    struct sensor_value accel[3];

    while (1) {
        // start a timer that expires when we need to grab the next value
        struct k_timer next_val_timer;
        k_timer_init(&next_val_timer, NULL, NULL);
        k_timer_start(&next_val_timer, K_USEC(time_between_samples_us), K_NO_WAIT);

        // read data from the sensor
        if (sensor_sample_fetch(lis2dh12) < 0) {
            printk("IIS2DLPC Sensor sample update error\n");
            return 1;
        }

        sensor_channel_get(lis2dh12, SENSOR_CHAN_ACCEL_XYZ, accel);

        // print over stdout
        printk("%.3f\t%.3f\t%.3f\r\n",
            sensor_value_to_double(&accel[0]),
            sensor_value_to_double(&accel[1]),
            sensor_value_to_double(&accel[2]));

        // Toggle the LED
        ret = gpio_pin_toggle_dt(&led);
        if (ret < 0) {
            printk("Could not toggle LED\n");
            return 1;
        }

        // Sleep for the defined time
        k_msleep(SLEEP_TIME_MS);

        // busy loop until next value should be grabbed
        while (k_timer_status_get(&next_val_timer) <= 0);
    }
}

/*
 * Copyright (c) 2016 Intel Corporation
 *
 * SPDX-License-Identifier: Apache-2.0
 */

// #include <zephyr/zephyr.h>
// #include <zephyr/drivers/gpio.h>

// /* 1000 msec = 1 sec */
// #define SLEEP_TIME_MS   50

// /* The devicetree node identifier for the "led0" alias. */
// #define LED0_NODE DT_ALIAS(led0)

/*
 * A build error on this line means your board is unsupported.
 * See the sample documentation for information on how to fix this.
 */
// static const struct gpio_dt_spec led = GPIO_DT_SPEC_GET(LED0_NODE, gpios);

// void main(void)
// {
// 	printf("Hello World! in maain");
// 	int ret;

// 	if (!device_is_ready(led.port)) {
// 		return;
// 	}

// 	ret = gpio_pin_configure_dt(&led, GPIO_OUTPUT_ACTIVE);
// 	if (ret < 0) {
// 		return;
// 	}

// 	while (1) {
// 		ret = gpio_pin_toggle_dt(&led);
// 		if (ret < 0) {
// 			return;
// 		}
// 		k_msleep(SLEEP_TIME_MS);
// 		printf("Hello World! %s\n", CONFIG_BOARD);
// 	}
// }
