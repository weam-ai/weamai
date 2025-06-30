
'use client'
import { useSubscriptionSSE } from '@/hooks/common/useSubscriptionSSE'
import React from 'react'

const SSESubscription = () => {
    useSubscriptionSSE()
    
  return (
    <div>`SSESubscription added`</div>
  )
}

export default SSESubscription