import { useState } from 'react';

const QuantitySelector = ({
    onChange,
    setSubTotal,
    setDiscount,
    setGrandTotal,
}) => {
    const [quantity, setQuantity] = useState(1);

    const handleInputChange = (event) => {
        const newQuantity = parseInt(event.target.value);
        if (!isNaN(newQuantity)) {
            setQuantity(newQuantity);
            onChange(newQuantity);
        }
    };

    const incrementQuantity = (event) => {
        event.preventDefault(); // Prevent default form submission behavior
        setQuantity((prevQuantity) => prevQuantity + 1);
        onChange(quantity + 1);
        setSubTotal((pre) => pre + 10);
        setGrandTotal((pre) => pre + 10);
    };

    const decrementQuantity = (event) => {
        event.preventDefault(); // Prevent default form submission behavior
        if (quantity > 1) {
            setQuantity((prevQuantity) => prevQuantity - 1);
            onChange(quantity - 1);
            setSubTotal((pre) => pre - 10);
            setGrandTotal((pre) => pre - 10);
        }
    };

    return (
        <div className="flex items-center gap-1.5">
            <button
                onClick={decrementQuantity}
                className="w-[30px] h-[30px] flex items-center justify-center rounded-custom border border-b11 hover:bg-b11 [&>svg]:w-3 [&>svg]:h-auto [&>svg]:fill-b6"
            >
                <svg
                    width="13"
                    height="3"
                    viewBox="0 0 13 3"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                >
                    <path
                        fillRule="evenodd"
                        clipRule="evenodd"
                        d="M0.77832 2.27832V0.147461H12.7783V2.27832H0.77832Z"
                    />
                </svg>
            </button>
            <input
                type="number"
                value={quantity}
                onChange={handleInputChange}
                min={1}
                className="text-font-16 font-semibold text-b2 border border-b11 rounded-custom text-center p-2 max-w-[55px] h-[30px] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
            />
            <button
                onClick={incrementQuantity}
                className="w-[30px] h-[30px] flex items-center justify-center rounded-custom border border-b11 hover:bg-b11 [&>svg]:w-3 [&>svg]:h-auto [&>svg]:fill-b6"
            >
                <svg
                    width="13"
                    height="13"
                    viewBox="0 0 13 13"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                >
                    <path d="M8.06403 5.14146C8.0072 5.14146 7.9527 5.11889 7.91251 5.0787C7.87233 5.03851 7.84975 4.98401 7.84975 4.92718V0.212891H5.70689V4.92718C5.70689 4.98401 5.68432 5.03851 5.64413 5.0787C5.60394 5.11889 5.54944 5.14146 5.49261 5.14146H0.77832V7.28432H5.49261C5.54944 7.28432 5.60394 7.3069 5.64413 7.34708C5.68432 7.38727 5.70689 7.44177 5.70689 7.4986V12.2129H7.84975V7.4986C7.84975 7.44177 7.87233 7.38727 7.91251 7.34708C7.9527 7.3069 8.0072 7.28432 8.06403 7.28432H12.7783V5.14146H8.06403Z" />
                </svg>
            </button>
        </div>
    );
};

export default QuantitySelector;
