'use client';
import { accessTokenViaRefresh } from '@/utils/handleAuth'
import React, { useEffect } from 'react'

const RefreshTokenClient = () => {
    useEffect(() => {
        accessTokenViaRefresh()
    }, [])
    return null
}

export default RefreshTokenClient