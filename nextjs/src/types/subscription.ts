type RazorpaySubscriptionOptions = {
    key: string;
    subscription_id?: string;
    order_id?: string;
    customer_id?: string;
    name: string;
    description: string;
    offer_id?: string;
    save?: boolean;
    saved_cards?: number;   
    subscription_card_change?: number;
    recurring?: number;
    handler: (response: any) => void;
    prefill: {
        name: string;
        email: string;
    };
    theme: {
        color: string;
    };
    method?: {
        card?: boolean;
        netbanking?: boolean;
        wallet?: boolean;
        upi?: boolean;
        paylater?: boolean;
        emi?: boolean;
    };
    config?: any;
    modal?: {
       
    };
}

export default RazorpaySubscriptionOptions;

export type SubscriptionActionStatusType = {
    companyId: string;
    startDate: string;
    status: string;
    totalMessageCount: boolean | number;
    msgCreditLimit: number;
    msgCreditUsed: number;
}