type ConfigurationButtonProps = {
    title: string;
    description: string;
    handleConnect: () => void;
    loading: boolean;
}

type DisconnectButtonProps = {
    title: string;
    description: string;
    handleDisconnect: () => void;
    loading: boolean;
}

export const ConfigurationButton = ({ title, description, handleConnect, loading }: ConfigurationButtonProps) => {
    return (
        <div className="space-y-4">
            <div className="bg-b2/10 p-4 rounded-lg">
                <h3 className="font-semibold text-font-16 mb-2">{`Connect to ${title}`}</h3>
                <p className="text-b6 text-font-14 mb-4">
                    {description}
                </p>
                <button
                    className="btn btn-black w-full"
                    onClick={handleConnect}
                    disabled={loading}
                >
                    {loading
                        ? 'Connecting...'
                        : `Connect to ${title}`}
                </button>
            </div>
        </div>
    )
}

export const DisconnectButton = ({ title, description, handleDisconnect, loading }: DisconnectButtonProps) => {
    return (
        <div className="space-y-6">
            <div className="border-t pt-4">
                <h3 className="font-semibold text-font-16 mb-3 text-red-600">
                    Danger Zone
                </h3>
                <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                    <p className="text-red-700 text-sm mb-3">
                        {description}
                    </p>
                    <button
                        className="btn btn-outline-red"
                        onClick={handleDisconnect}
                        disabled={loading}
                    >
                        {loading
                            ? 'Disconnecting...'
                            : `Disconnect ${title}`}
                    </button>
                </div>
            </div>
        </div>
    )
}