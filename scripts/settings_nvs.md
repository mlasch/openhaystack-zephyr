# Settings with NVS backend

Settings are stored in the storage partition in the flash. 

/* In the NVS backend, each setting is stored in two NVS entries:
 *      1. setting's name
 *      2. setting's value
 *
 * The NVS entry ID for the setting's value is determined implicitly based on
 * the ID of the NVS entry for the setting's name, once that is found. The
 * difference between name and value ID is constant and equal to
 * NVS_NAME_ID_OFFSET.

e.g. nvs name entry is 0x8001, then the name entry is 0x8001 + NVS_NAME_ID_OFFSET = 0xc001
 *
 * Setting's name entries start from NVS_NAMECNT_ID + 1. The entry at
 * NVS_NAMECNT_ID is used to store the largest name ID in use.
 *
 * Deleted records will not be found, only the last record will be
 * read.

*/

#define NVS_NAMECNT_ID 0x8000 32768
#define NVS_NAME_ID_OFFSET 0x4000 16384

``` C
/* Allocation Table Entry /
struct nvs_ate {
    uint16_t id;    / data id /
    uint16_t offset;    / data offset within sector /
    uint16_t len;    / data len within sector /
    uint8_t part;    / part of a multipart data - future extension /
    uint8_t crc8;    / crc8 check of the entry */
} __packed;
```
Sector close ate
ff ff 00 00 00 00 ff 5c

 * id: 0xffff
 * offset: 0x0000 offset points to location at ate multiple from sector size
 * len: 0x0000
 * part: 0xff
 * crc8: 0x5c

# Examples
NVS with four entries, data: BBB... name: AAAA, data: XXX..., name: BBBB

```
00000000  ff ff ff ff ff ff ff ff  ff ff ff ff ff ff ff ff  |................|
*         Largest name ID in use = 8001
000fc000  01 80 42 42 42 42 42 42  42 42 42 42 42 42 42 42  |..BBBBBBBBBBBBBB|
000fc010  42 42 42 42 42 42 42 42  42 42 42 42 42 42 41 41  |BBBBBBBBBBBBBBAA|
000fc020  41 41 58 58 58 58 58 58  58 58 58 58 58 58 58 58  |AAXXXXXXXXXXXXXX|
000fc030  58 58 58 58 58 58 58 58  58 58 58 58 58 58 02 80  |XXXXXXXXXXXXXX..|
000fc040  58 58 58 58 58 58 58 58  58 58 58 58 58 58 58 58  |XXXXXXXXXXXXXXXX|
000fc050  58 58 58 58 58 58 58 58  58 58 58 58 42 42 42 42  |XXXXXXXXXXXXBBBB|
000fc060  ff ff ff ff ff ff ff ff  ff ff ff ff ff ff ff ff  |................|
*
000fcfb0  ff ff ff ff ff ff ff ff  02 80 5c 00 04 00 ff 25  |..........\....%|
000fcfc0  02 c0 40 00 1c 00 ff 04  00 80 3e 00 02 00 ff 89  |..@.......>.....|
000fcfd0  01 c0 22 00 1c 00 ff 0a  01 80 1e 00 04 00 ff 4f  |.."............O|
000fcfe0  01 c0 02 00 1c 00 ff 6e  00 80 00 00 02 00 ff 8d  |.......n........|
000fcff0  ff ff 00 00 00 00 ff 5c  ff ff ff ff ff ff ff ff  |.......\........|
000fd000  ff ff ff ff ff ff ff ff  ff ff ff ff ff ff ff ff  |................|
*
00200000
```

NVS with four entries, data1, name1
```
00000000  ff ff ff ff ff ff ff ff  ff ff ff ff ff ff ff ff  |................|
*
000fc000  01 80 42 42 42 42 42 42  42 42 42 42 42 42 42 42  |..BBBBBBBBBBBBBB|
000fc010  42 42 42 42 42 42 42 42  42 42 42 42 42 42 41 41  |BBBBBBBBBBBBBBAA|
000fc020  41 41 ff ff ff ff ff ff  ff ff ff ff ff ff ff ff  |AA..............|
000fc030  ff ff ff ff ff ff ff ff  ff ff ff ff ff ff ff ff  |................|
*
000fcfd0  ff ff ff ff ff ff ff ff  01 80 1e 00 04 00 ff 4f  |...............O|
000fcfe0  01 c0 02 00 1c 00 ff 6e  00 80 00 00 02 00 ff 8d  |.......n........|
000fcff0  ff ff 00 00 00 00 ff 5c  ff ff ff ff ff ff ff ff  |.......\........|
000fd000  ff ff ff ff ff ff ff ff  ff ff ff ff ff ff ff ff  |................|
*
00200000
```
