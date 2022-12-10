rsync -arvz -e 'ssh -p 10022' ../obj/home/evgeny/shiny/src/arm64.aarch64/sys/GENERIC/kernel free@localhost:~/qemu/kernel.img
ssh -p 10022 free@localhost -C "sudo cp ~/qemu/kernel.img /boot/kernel/kernel && sudo reboot"
