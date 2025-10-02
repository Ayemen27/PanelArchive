# 🔒 Security Hardening Guide - aaPanel

## 📋 جدول المحتويات

1. [نظرة عامة](#نظرة-عامة)
2. [البدء السريع](#البدء-السريع)
3. [System Hardening](#system-hardening)
4. [SSH Security](#ssh-security)
5. [Automatic Updates](#automatic-updates)
6. [Audit Logging](#audit-logging)
7. [Password Policies](#password-policies)
8. [File Permissions](#file-permissions)
9. [Security Checks](#security-checks)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

---

## 🌟 نظرة عامة

**Security Hardening** هو عملية تشديد أمان النظام من خلال تقليل سطح الهجوم (attack surface) وتطبيق best practices الأمنية.

### 🎯 الأهداف

- ✅ حماية النظام من الاختراق
- ✅ منع الوصول غير المصرح به
- ✅ تقليل الثغرات الأمنية
- ✅ Compliance مع معايير الأمان
- ✅ Logging شامل للأنشطة المشبوهة

### 📦 المكونات

هذا الدليل يغطي:

1. **setup_security_hardening.sh** - سكريبت إعداد شامل
2. **security_check.sh** - سكريبت فحص الثغرات
3. **Best practices** - توصيات أمنية

---

## 🚀 البدء السريع

### التثبيت الأساسي

```bash
# 1. تنزيل السكريبتات
chmod +x setup_security_hardening.sh security_check.sh

# 2. تشغيل Security Hardening
sudo ./setup_security_hardening.sh -y

# 3. التحقق من النتائج
sudo ./security_check.sh

# 4. فحص سريع
sudo security-check
```

### الاستخدام التفاعلي

```bash
# Interactive mode (يسأل أسئلة)
sudo ./setup_security_hardening.sh

# Non-interactive mode (بدون أسئلة)
sudo ./setup_security_hardening.sh -y

# تخطي automatic updates
sudo ./setup_security_hardening.sh --skip-updates
```

---

## 🛡️ System Hardening

### Kernel Parameters (sysctl)

يتم تطبيق kernel hardening عبر `/etc/sysctl.d/99-security-hardening.conf`:

#### Network Security

| Parameter | Value | الوصف |
|-----------|-------|--------|
| `net.ipv4.tcp_syncookies` | 1 | SYN Flood Protection |
| `net.ipv4.conf.all.accept_redirects` | 0 | منع ICMP Redirects |
| `net.ipv4.conf.all.accept_source_route` | 0 | منع Source Routing |
| `net.ipv4.conf.all.rp_filter` | 1 | Reverse Path Filtering |
| `net.ipv4.conf.all.log_martians` | 1 | Log Suspicious Packets |

#### Memory & Process Protection

| Parameter | Value | الوصف |
|-----------|-------|--------|
| `kernel.randomize_va_space` | 2 | ASLR (Address Space Layout Randomization) |
| `kernel.dmesg_restrict` | 1 | منع kernel info leak |
| `kernel.kptr_restrict` | 2 | إخفاء Kernel Pointers |
| `kernel.yama.ptrace_scope` | 1 | تقييد debugging |
| `fs.suid_dumpable` | 0 | تعطيل Core Dumps |

#### File System Security

| Parameter | Value | الوصف |
|-----------|-------|--------|
| `fs.protected_symlinks` | 1 | حماية Symlinks |
| `fs.protected_hardlinks` | 1 | حماية Hardlinks |
| `fs.protected_fifos` | 2 | حماية FIFOs |
| `fs.protected_regular` | 2 | حماية Regular Files |

### التطبيق اليدوي

```bash
# عرض الإعدادات الحالية
sysctl -a | grep -E "net.ipv4|kernel|fs"

# تطبيق إعداد واحد
sysctl -w net.ipv4.tcp_syncookies=1

# تطبيق جميع الإعدادات
sysctl -p /etc/sysctl.d/99-security-hardening.conf

# التحقق
sysctl net.ipv4.tcp_syncookies
```

---

## 🔐 SSH Security

### التحسينات المطبقة

#### 1. Disable Root Login

```bash
# في /etc/ssh/sshd_config
PermitRootLogin no
```

**لماذا؟**
- منع الهجمات المباشرة على حساب root
- إجبار المستخدمين على استخدام sudo (audit trail)

#### 2. Key-Based Authentication (اختياري)

```bash
# تعطيل Password Authentication
PasswordAuthentication no
```

**⚠️ تحذير:** تأكد من وجود SSH keys قبل تفعيل هذا!

**إعداد SSH Keys:**

```bash
# على جهازك المحلي
ssh-keygen -t ed25519 -C "your_email@example.com"

# نسخ المفتاح للخادم
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@server

# اختبار
ssh -i ~/.ssh/id_ed25519 user@server
```

#### 3. Additional Hardening

| Setting | Value | الوصف |
|---------|-------|--------|
| `Protocol` | 2 | SSH Protocol 2 only |
| `X11Forwarding` | no | تعطيل X11 |
| `MaxAuthTries` | 3 | 3 محاولات فقط |
| `ClientAliveInterval` | 300 | Timeout بعد 5 دقائق |
| `ClientAliveCountMax` | 2 | 2 pings قبل disconnect |
| `PermitEmptyPasswords` | no | منع كلمات مرور فارغة |

### التطبيق

```bash
# تحرير SSH config
sudo nano /etc/ssh/sshd_config

# التحقق من الصحة
sudo sshd -t

# إعادة تحميل SSH
sudo systemctl reload sshd

# التأكد من عدم قطع الاتصال!
# افتح terminal جديد واختبر قبل إغلاق الحالي
```

---

## 🔄 Automatic Security Updates

### Ubuntu/Debian (unattended-upgrades)

#### التثبيت

```bash
sudo apt-get update
sudo apt-get install -y unattended-upgrades apt-listchanges
```

#### التكوين

**ملف `/etc/apt/apt.conf.d/50unattended-upgrades`:**

```bash
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
};

Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
```

**ملف `/etc/apt/apt.conf.d/20auto-upgrades`:**

```bash
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
```

#### الاختبار

```bash
# Dry run
sudo unattended-upgrades --dry-run -d

# التحقق من الحالة
sudo systemctl status unattended-upgrades

# السجلات
sudo cat /var/log/unattended-upgrades/unattended-upgrades.log
```

### CentOS/RHEL (yum-cron)

#### التثبيت

```bash
sudo yum install -y yum-cron
```

#### التكوين

```bash
# تحرير /etc/yum/yum-cron.conf
sudo nano /etc/yum/yum-cron.conf

# التغييرات المطلوبة:
apply_updates = yes
update_cmd = security
```

#### التشغيل

```bash
sudo systemctl enable yum-cron
sudo systemctl start yum-cron

# التحقق
sudo systemctl status yum-cron
```

---

## 📝 Audit Logging

### auditd - Linux Audit Daemon

#### التثبيت

```bash
# Ubuntu/Debian
sudo apt-get install -y auditd audispd-plugins

# CentOS/RHEL
sudo yum install -y audit
```

#### Audit Rules

**ملف `/etc/audit/rules.d/security-hardening.rules`:**

```bash
# Buffer Size
-b 8192

# Failure Mode (1 = print, 2 = panic)
-f 1

# Authentication
-w /var/log/faillog -p wa -k auth_failures
-w /etc/passwd -p wa -k passwd_changes
-w /etc/shadow -p wa -k shadow_changes
-w /etc/sudoers -p wa -k sudoers_changes

# System Control
-w /sbin/shutdown -p x -k system_shutdown
-w /sbin/reboot -p x -k system_reboot

# Process Execution
-a always,exit -F arch=b64 -S execve -k process_execution

# File Changes
-w /etc/ -p wa -k etc_changes
-w /www/server/panel/ -p wa -k aapanel_changes

# Network Activity
-a always,exit -F arch=b64 -S socket -S connect -k network

# Privilege Escalation
-a always,exit -F arch=b64 -S setuid -S setgid -k privilege_escalation

# Make immutable
-e 2
```

#### الاستخدام

```bash
# تحميل القواعد
sudo augenrules --load

# عرض القواعد النشطة
sudo auditctl -l

# البحث في logs
sudo ausearch -k passwd_changes
sudo ausearch -k auth_failures
sudo ausearch -ts today -k network

# عرض ملخص
sudo aureport --summary

# تقرير المصادقة
sudo aureport -au

# متابعة logs
sudo tail -f /var/log/audit/audit.log
```

#### أمثلة عملية

```bash
# من قام بتغيير /etc/passwd؟
sudo ausearch -f /etc/passwd -i

# محاولات sudo الفاشلة
sudo ausearch -m USER_AUTH -sv no

# نشاط شبكي لمستخدم معين
sudo ausearch -ua <username> -k network

# Process execution في آخر ساعة
sudo ausearch -ts recent -k process_execution
```

---

## 🔑 Password Policies

### Login.defs Configuration

**ملف `/etc/login.defs`:**

| Setting | Value | الوصف |
|---------|-------|--------|
| `PASS_MAX_DAYS` | 90 | كلمة المرور تنتهي بعد 90 يوم |
| `PASS_MIN_DAYS` | 1 | يوم واحد قبل تغيير كلمة المرور |
| `PASS_MIN_LEN` | 12 | 12 حرف كحد أدنى |
| `PASS_WARN_AGE` | 7 | تحذير 7 أيام قبل الانتهاء |

### Password Quality (pwquality)

**ملف `/etc/security/pwquality.conf`:**

```bash
# Password Requirements
minlen = 12          # 12 حرف كحد أدنى
dcredit = -1         # رقم واحد على الأقل
ucredit = -1         # حرف كبير واحد على الأقل
ocredit = -1         # رمز خاص واحد على الأقل
lcredit = -1         # حرف صغير واحد على الأقل
minclass = 3         # 3 فئات مختلفة على الأقل
maxrepeat = 2        # لا أكثر من حرفين متكررين
maxsequence = 3      # لا أكثر من 3 أحرف متسلسلة (abc, 123)
```

### تطبيق على المستخدمين الحاليين

```bash
# تغيير max days لمستخدم
sudo chage -M 90 username

# عرض معلومات كلمة المرور
sudo chage -l username

# إجبار تغيير كلمة المرور عند تسجيل الدخول القادم
sudo chage -d 0 username
```

---

## 📁 File Permissions

### Critical System Files

| File | Permissions | Owner:Group |
|------|-------------|-------------|
| `/etc/passwd` | 644 | root:root |
| `/etc/shadow` | 600 | root:root |
| `/etc/group` | 644 | root:root |
| `/etc/gshadow` | 600 | root:root |
| `/etc/ssh/sshd_config` | 600 | root:root |
| `/etc/sudoers` | 440 | root:root |

### aaPanel Directories

```bash
# aaPanel main directory
sudo chown -R www:www /www/server/panel
sudo chmod 750 /www/server/panel

# Logs
sudo chmod 640 /www/server/panel/logs/*.log
sudo chown www:www /www/server/panel/logs/*.log

# Config files
sudo chmod 600 /www/server/panel/config/*.conf
```

### البحث عن مشاكل الصلاحيات

```bash
# World-writable files
sudo find / -xdev -type f -perm -002 ! -path "/proc/*" ! -path "/sys/*"

# Unowned files
sudo find / -xdev \( -nouser -o -nogroup \) ! -path "/proc/*" ! -path "/sys/*"

# SUID/SGID files
sudo find / -xdev \( -perm -4000 -o -perm -2000 \) -type f

# Files writable by group
sudo find / -xdev -type f -perm -020 ! -path "/proc/*" ! -path "/sys/*"
```

---

## 🧪 Security Checks

### استخدام security_check.sh

```bash
# فحص عادي
sudo ./security_check.sh

# فحص مفصل
sudo ./security_check.sh --detailed

# Output JSON
sudo ./security_check.sh --json > security-report.json
```

### فحص يدوي

#### 1. Network Security

```bash
# المنافذ المفتوحة
sudo ss -tuln | grep LISTEN

# Firewall status
sudo ufw status verbose

# Active connections
sudo ss -tunap
```

#### 2. User Accounts

```bash
# حسابات بدون كلمات مرور
sudo awk -F: '($2 == "") {print $1}' /etc/shadow

# UID 0 accounts (غير root)
sudo awk -F: '($3 == "0") {print $1}' /etc/passwd | grep -v "^root$"

# آخر تسجيل دخول
sudo lastlog

# محاولات فاشلة
sudo grep "Failed password" /var/log/auth.log | tail -20
```

#### 3. Services

```bash
# الخدمات النشطة
sudo systemctl list-units --type=service --state=running

# Listening services
sudo netstat -tulpn

# Process tree
sudo pstree -p
```

---

## ✅ Best Practices

### 1. Regular Updates

```bash
# يومياً: فحص التحديثات
sudo apt update && sudo apt list --upgradable

# أسبوعياً: تطبيق التحديثات الأمنية
sudo apt upgrade -y

# شهرياً: تحديث كامل
sudo apt dist-upgrade -y
```

### 2. Log Monitoring

```bash
# فحص يومي للسجلات
sudo journalctl -p err -b
sudo grep "Failed password" /var/log/auth.log | tail -50
sudo ausearch -ts today -m USER_AUTH -sv no
```

### 3. Backup Configuration

```bash
# نسخ احتياطي للإعدادات الحرجة
sudo tar -czf /root/config-backup-$(date +%Y%m%d).tar.gz \
    /etc/ssh/sshd_config \
    /etc/sysctl.d/ \
    /etc/audit/rules.d/ \
    /etc/fail2ban/
```

### 4. Security Audit Schedule

| Frequency | Task |
|-----------|------|
| **يومياً** | فحص failed logins، مراجعة audit logs |
| **أسبوعياً** | `security_check.sh --detailed`، مراجعة updates |
| **شهرياً** | Full security audit، vulnerability scan |
| **ربع سنوي** | Password rotation، review user accounts |

### 5. Incident Response

```bash
# عند اكتشاف نشاط مشبوه:

# 1. عزل المشكلة
sudo ufw deny from <suspicious_IP>
sudo fail2ban-client set <jail> banip <IP>

# 2. جمع الأدلة
sudo ausearch -i -ts <time> > incident-$(date +%Y%m%d).log
sudo journalctl --since "<time>" > system-$(date +%Y%m%d).log

# 3. تحليل
sudo grep <suspicious_IP> /var/log/auth.log
sudo ausearch -k network | grep <suspicious_IP>

# 4. إصلاح
# ... حسب نوع المشكلة
```

---

## 🔧 Troubleshooting

### مشكلة: SSH Lockout

**الأعراض:** لا يمكن تسجيل الدخول عبر SSH

**الحل:**

```bash
# من console (لا من SSH):

# 1. التحقق من SSH status
sudo systemctl status sshd

# 2. التحقق من config
sudo sshd -t

# 3. السجلات
sudo journalctl -u sshd -n 50

# 4. استعادة config
sudo cp /root/security-hardening-backup-*/sshd_config /etc/ssh/
sudo systemctl restart sshd
```

### مشكلة: auditd يملأ الديسك

**الأعراض:** مساحة القرص ممتلئة بسبب `/var/log/audit/`

**الحل:**

```bash
# 1. فحص المساحة
sudo du -sh /var/log/audit/

# 2. تقليل buffer size
sudo nano /etc/audit/rules.d/security-hardening.rules
# غيّر: -b 8192 إلى -b 4096

# 3. Log rotation
sudo nano /etc/audit/auditd.conf
# max_log_file_action = rotate
# num_logs = 5

# 4. إعادة تحميل
sudo service auditd restart
```

### مشكلة: High Load بسبب sysctl

**الأعراض:** النظام بطيء بعد تطبيق sysctl

**الحل:**

```bash
# 1. التحقق من القيم الحالية
sysctl -a | grep -E "tcp_|mem_"

# 2. استعادة defaults
sudo cp /root/security-hardening-backup-*/sysctl.conf /etc/
sudo sysctl -p

# 3. تطبيق تدريجي
# طبّق إعداد واحد في كل مرة واختبر
```

### مشكلة: Password Policy صارمة جداً

**الأعراض:** المستخدمون لا يستطيعون تعيين كلمات مرور

**الحل:**

```bash
# تخفيف المتطلبات مؤقتاً
sudo nano /etc/security/pwquality.conf

# تقليل minlen
minlen = 8  # بدلاً من 12

# السماح بـ fewer classes
minclass = 2  # بدلاً من 3

# إعادة اختبار
passwd  # اختبر تغيير كلمة المرور
```

---

## 📚 الموارد الإضافية

### Documentation

- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)
- [NIST Security Guidelines](https://www.nist.gov/cyberframework)
- [OWASP Security Practices](https://owasp.org/)

### Tools

- **Lynis** - Security auditing tool
- **Tiger** - Security audit and intrusion detection
- **ClamAV** - Antivirus
- **rkhunter** - Rootkit detection

### Commands Reference

```bash
# Security scanning
sudo lynis audit system

# Rootkit detection
sudo rkhunter --check

# Malware scanning
sudo clamscan -r /home

# Password strength testing
echo "password123" | pwscore
```

---

## 📞 الحصول على مساعدة

### Logs المفيدة

```bash
# System logs
sudo journalctl -xe
sudo journalctl -u ssh -f

# Authentication logs
sudo tail -f /var/log/auth.log   # Ubuntu/Debian
sudo tail -f /var/log/secure      # CentOS/RHEL

# Audit logs
sudo tail -f /var/log/audit/audit.log

# aaPanel logs
sudo tail -f /www/server/panel/logs/error.log
```

### الأوامر السريعة

```bash
# فحص سريع
sudo security-check

# فحص مفصل
sudo ./security_check.sh --detailed

# Fail2Ban status
sudo fail2ban-client status

# auditd rules
sudo auditctl -l

# Update check
sudo apt list --upgradable  # Ubuntu/Debian
sudo yum check-update       # CentOS/RHEL
```

---

## ✅ Checklist النهائية

قبل اعتبار النظام "محمّي":

- [ ] ✅ System hardening (sysctl) مطبق
- [ ] ✅ SSH hardening مكتمل
- [ ] ✅ Root login معطّل
- [ ] ✅ Firewall (UFW) نشط
- [ ] ✅ Fail2Ban يعمل مع jails نشطة
- [ ] ✅ Automatic updates مكوّنة
- [ ] ✅ auditd يعمل مع rules شاملة
- [ ] ✅ Password policies محسّنة
- [ ] ✅ File permissions صحيحة
- [ ] ✅ Unnecessary services معطّلة
- [ ] ✅ Security checks تمر بنجاح (>90%)
- [ ] ✅ Backups للإعدادات موجودة
- [ ] ✅ Log monitoring مفعّل
- [ ] ✅ Documentation محدّثة

---

**🎉 تهانينا! نظامك الآن محمي بشكل شامل.**

**آخر تحديث:** 1 أكتوبر 2025  
**الحالة:** ✅ جاهز للإنتاج
