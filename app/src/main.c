/*
 * OpenHaystack Zephyr firmware - Track your personal Bluetooth devices via
 * Apple's Find My network
 *
 * Copyright (c) 2021 Koen Vervloesem <koen@vervloesem.eu>
 * Copyright (c) 2025 Marc Lasch <mlasch@mailbox.org>
 *
 * SPDX-License-Identifier: MIT
 */

#if defined(CONFIG_BT)
#include <zephyr/bluetooth/addr.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/hci.h>
#endif
#include <stddef.h>
#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zephyr/settings/settings.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/util.h>
#include <zephyr/types.h>

#include "openhaystack.h"

LOG_MODULE_REGISTER(app, LOG_LEVEL_DBG);

#define PUBLIC_KEY_SIZE 28
#define MAC_ADDRESS_SIZE 6
// Don't make `const`, so we can replace the key in the compiled bin file
static uint8_t public_key[PUBLIC_KEY_SIZE] = {0};

static bt_addr_le_t device_address = {BT_ADDR_LE_RANDOM, {{0}}};

static int load_public_key(uint8_t *pk, size_t key_size) {
    int ret;
    ret = settings_subsys_init();
    if (ret) {
        LOG_ERR("Settings subsys init failed: %d\n", ret);
        return ret;
    }
    /*
            ret = settings_save_one("AAAA", pk, key_size);
            if (ret < 0) {
                    printk("Failed to save public key (err %d)\n", ret);
                    return ret;
            }
            ret = settings_save_one("BBBB", pk, key_size);
            if (ret < 0) {
                    printk("Failed to save public key (err %d)\n", ret);
                    return ret;
            }
    */
    ret = settings_load_one("airtag/public_key", pk, key_size);
    LOG_DBG("Loaded public key size %zu bytes\n", ret);

    return ret;
}

int main(void) {
    int err, bt_id;

    LOG_INF("Starting OpenHaystack firmware...\n");

    int ret = load_public_key(public_key, sizeof(public_key));
    if (ret < 0) {
        LOG_ERR("Failed to load public key (err %d)\n", ret);
        return -1;
    }

    LOG_HEXDUMP_DBG(public_key, sizeof(public_key), "public_key");

    // Set advertisement data
    of_set_manufacturer_data_from_key(of_manufacturer_data, public_key);

    // Set default address
    of_set_address_from_key(&device_address, public_key);
#if defined(CONFIG_BT)
    bt_id = bt_id_create(&device_address, NULL);
    if (bt_id < 0) {
        LOG_ERR("Can't create new identity (err %d)\n", bt_id);
        return -1;
    } else {
        LOG_INF("Created new identity %d\n", bt_id);
    }

    // Initialize the Bluetooth subsystem
    err = bt_enable(NULL);
    if (err) {
        LOG_ERR("Bluetooth init failed (err %d)\n", err);
    }

    LOG_INF("Bluetooth initialized\n");

    // Start advertising
    of_adv_param.id = 0;
    err = bt_le_adv_start(&of_adv_param, of_advertising_data, ARRAY_SIZE(of_advertising_data), NULL,
                          0);
    if (err) {
        LOG_ERR("Advertising failed to start (err %d)\n", err);
        return -1;
    }
#endif
    return 0;
}
