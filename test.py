# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import sys

from typing import List

from alibabacloud_tea_util.client import Client as UtilClient
from alibabacloud_tea_util import models as util_models
from alibabacloud_darabonba_number.client import Client as NumberClient
from alibabacloud_tea_console.client import Client as ConsoleClient
from alibabacloud_darabonba_array.client import Client as ArrayClient
from alibabacloud_ecs20140526.client import Client as EcsClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ecs20140526 import models as ecs_models


class Sample:
    def __init__(self):
        pass

    @staticmethod
    def create_client(
            access_key_id: str,
            access_key_secret: str,
            region_id: str,
    ) -> EcsClient:
        config = open_api_models.Config()
        config.access_key_id = access_key_id
        config.access_key_secret = access_key_secret
        config.region_id = region_id
        return EcsClient(config)

    @staticmethod
    def launch_instance(
            instance_type: str,
            image_id: str,
            region_id: str,
            security_group_id: str,
            instance_name: str,
            description: str,
            zone_id: str,
            category: str,
            v_switch_id: str,
            instance_charge_type: str,
            period_unit: str,
            amount: int,
            dry_run: bool,
            client: EcsClient,
    ) -> List[str]:
        """
        创建并运行实例
        """
        request = ecs_models.RunInstancesRequest(
            region_id=region_id,
            instance_type=instance_type,
            image_id=image_id,
            security_group_id=security_group_id,
            instance_name=instance_name,
            description=description,
            zone_id=zone_id,
            v_switch_id=v_switch_id,
            amount=amount,
            instance_charge_type=instance_charge_type,
            period_unit=period_unit,
            dry_run=dry_run,
            system_disk=ecs_models.RunInstancesRequestSystemDisk(
                category=category
            )
        )
        ConsoleClient.log(f'--------创建实例开始-----------')
        responces = client.run_instances(request)
        ConsoleClient.log(f'-----------创建实例成功，实例ID:{UtilClient.to_jsonstring(responces.body.instance_id_sets.instance_id_set)}--------------')
        return responces.body.instance_id_sets.instance_id_set

    @staticmethod
    def destroy_instance(
            client: EcsClient,
            instance_id: str,
    ) -> bool:
        """
        查询实例状态
        """
        delete_instance_request = ecs_models.DeleteInstanceRequest(
            instance_id=instance_id,
            force=True,
        )

        ConsoleClient.log(f'实例: {instance_id}, 开始delete.')
        try:
            runtime = util_models.RuntimeOptions()
            response = client.delete_instance_with_options(delete_instance_request, runtime)
        except Exception as error:
            # 如有需要，请打印 error
            ConsoleClient.log(f"failed to delete instance: {error}")
            return False

        ConsoleClient.log(f'实例: {instance_id}, delete 成功：{response}')
        return True

    @staticmethod
    def await_instance_status_to_running(
            client: EcsClient,
            region_id: str,
            instance_ids: List[str],
    ) -> bool:
        """
        等待实例状态为 Running
        """
        time = 0
        flag = True
        while flag and NumberClient.lt(time, 10):
            flag = False
            instance_status_list = Sample.describe_instance_status(client, region_id, instance_ids)
            for instance_status in instance_status_list:
                if not UtilClient.equal_string(instance_status, 'Running'):
                    UtilClient.sleep(2000)
                    flag = True
            time = NumberClient.add(time, 1)
        return NumberClient.lt(time, 10)

    # example return: [{"InstanceId": "i-uf6bhilatj9m2wlkgfy1", "Status": "Running"}
    @staticmethod
    def describe_instance_status(
            client: EcsClient,
            region_id: str,
            instance_ids: List[str],
    ) -> List[str]:
        """
        查询实例状态
        """
        request = ecs_models.DescribeInstanceStatusRequest(
            region_id=region_id,
            instance_id=instance_ids
        )
        responces = client.describe_instance_status(request)
        instance_status_list = responces.body.instance_statuses.instance_status
        ConsoleClient.log(f'实例: {instance_ids}, 查询状态成功。状态为: {UtilClient.to_jsonstring(instance_status_list)}')
        status_list = {}
        for instance_status in instance_status_list:
            status_list = ArrayClient.concat(status_list, [
                instance_status.status
            ])
        return status_list

    @staticmethod
    def get_instance_ip(
            client: EcsClient,
            region_id: str,
            instance_id: str,
    ) -> str:
        """
        查询实例状态
        """
        ConsoleClient.log(f'实例: {instance_id}, 获取IP。')
        request = ecs_models.DescribeInstancesRequest(
            region_id=region_id,
            instance_ids=[instance_id]
        )
        response = client.describe_instances(request)
        instance = response.body.instances.instance[0]
        ip = instance.network_interfaces.network_interface[0].primary_ip_address
        ConsoleClient.log(f'实例: {instance_id}, IP: {ip}')
        return ip

    @staticmethod
    def main() -> None:
        """
        创建实例 ->
        查询实例状态running->
        拿到private IP
        销毁机器
        """
        # 实例所属的地域ID
        region_id = 'cn-shanghai'
        # 实例的资源规格
        instance_type = 'ecs.n4.small'
        # 镜像ID
        image_id = 'centos_7_9_x64_20G_alibase_20221028.vhd'
        # 安全组
        security_group_id = 'sg-uf63jawzncdbxq6bk1kh'
        # 实例名称
        instance_name = 'yikker'
        description = 'test'
        zone_id = 'cn-shanghai-a'
        # 系统盘的磁盘种类
        category = 'cloud_efficiency'
        # 实例的计费方式
        instance_charge_type = 'PostPaid'
        # 购买资源的时长单位
        period_unit = 'Hourly'
        # 虚拟交换机ID
        v_switch_id = 'vsw-uf61b5od26m8dzhmb8fl1'
        # 创建ECS实例的数量
        amount = 1
        # 预检请求
        # true：发送检查请求，不会创建实例。检查项包括是否填写了必需参数、请求格式、业务限制和ECS库存。如果检查不通过，则返回对应错误。如果检查通过，则返回DryRunOperation错误。
        # false：发送正常请求，通过检查后直接创建实例。
        dry_run = False
        # AK/SK
        access_key_id = 'change_me'
        access_key_secret = 'change_me'
        client = Sample.create_client(access_key_id, access_key_secret, region_id)

        # 创建并与运行实例
        instance_ids = Sample.launch_instance(instance_type, image_id, region_id, security_group_id, instance_name, description, zone_id, category, v_switch_id, instance_charge_type, period_unit,
                                              amount, dry_run, client)
        # 等待实例创建成功
        UtilClient.sleep(2000)
        if not dry_run and not UtilClient.equal_number(ArrayClient.size(instance_ids), 0):
            if Sample.await_instance_status_to_running(client, region_id, instance_ids):
                # get instance IP
                for id in instance_ids:
                    Sample.get_instance_ip(client, region_id, id)
                    Sample.destroy_instance(client, id)
                pass
            else:
                ConsoleClient.log(f'实例状态异常，运行结束')


if __name__ == '__main__':
    Sample.main()
