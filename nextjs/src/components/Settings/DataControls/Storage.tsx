import { getStorageAction } from '@/actions/storage'
import React from 'react'
import DoughnutChartStorage from '../DoughnutChartStorage';
import { bytesToMegabytes } from '@/utils/common';
import StorageAction from './StorageAction';

const Storage = async () => {
    const { data } = await getStorageAction();
    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mt-7">
            <div className="border border-b11 rounded-custom p-5">
                <div className="relative flex items-center justify-center">
                    <DoughnutChartStorage
                        used={bytesToMegabytes(data?.used)}
                        total={bytesToMegabytes(data?.total)}
                    />
                </div>
            </div>
            <div className="flex flex-col justify-center items-center">
                <p className="mb-2.5 text-font-16 font-normal text-b2">
                    Need more storage?
                </p>
                <StorageAction />
            </div>
        </div>
    )
}

export default Storage