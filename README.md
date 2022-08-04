# V2free自动签到,并发送邮件
v2free checkin ,send email
## 使用教程
点击Fork按钮将项目Fork到自己仓库

## 配置参数

依次点击上栏【Setting】->【Security】->【Secrets】->【Actions】->【New repository secrets】 添加账号和密码等信息，示例如下：


    |key    |value                     |

    |USER   |123@qq.com,567@outlook.com|
    |PWD    |ccc,aaa                   |
    |remail |abc@163.com               |
    |semail |cdc@163.com               |
    |secode |sakdjdiunerhv             |


## 说明
* 支持多账号，账号之间与密码之间用半角逗号分隔，账号与密码的个数要对应。

* 脚本会在北京时间08:00执行一次(Github定时任务会有20min左右延迟)，或者自己action亦可手动执行一次(无延迟)。
