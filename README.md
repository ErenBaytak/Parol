# Parol Repair 4.0.0

Debian/Ubuntu tabanlı sistemler için çok dilli sistem onarım aracı.
İki arayüz: terminal (curses) ve Windows Recovery tarzı grafik arayüz.

## Komutlar
| Komut | İşlev |
|---|---|
| `parol` | Terminal arayüzü |
| `parol gui` / `parol-gui` | Recovery grafik arayüzü |
| `parol log` | Günlüğün son 200 satırı |
| `parol version` | Sürüm + lisans |
| `parol-tui`, `parolgui`, `prepair` | Alias kısayolları |

## Dil
Sistem dili otomatik algılanır (tr/en). Zorlamak için: `PAROL_LANG=en parol`

## Güvenlik
Yüksek riskli işlemler onay ister. Otomatik Onarım yalnızca güvenli/orta
riskli işlemleri çalıştırır; GRUB, initramfs, display-manager gibi işler
otomatik moda dahil edilmez.

## Kaldırma
`sudo apt remove --purge parol-repair`

---
Copyright (C) 2026 **Ermedsoft - Eren Baytak Yazılım**
GNU GPL v3 or later — Açık kaynak yazılım.
