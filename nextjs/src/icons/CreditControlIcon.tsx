import { SvgProps } from "@/types/assets";

const CreditControlIcon = ({ height, width, className }: SvgProps) => {
    return (
      <svg
        className={className}
        width={width}
        height={height}
        viewBox="0 0 512 352"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path d="M456 0H56C25.122 0 0 25.122 0 56V296C0 326.878 25.122 352 56 352H456C486.878 352 512 326.878 512 296V56C512 25.122 486.878 0 456 0ZM56 32H456C469.233 32 480 42.767 480 56V88H32V56C32 42.767 42.767 32 56 32ZM456 320H56C42.767 320 32 309.233 32 296V120H480V296C480 309.233 469.233 320 456 320Z" />
        <path d="M112 272H96C87.164 272 80 264.836 80 256V240C80 231.164 87.164 224 96 224H112C120.836 224 128 231.164 128 240V256C128 264.836 120.836 272 112 272Z" />
      </svg>
    );
  };
  export default CreditControlIcon;