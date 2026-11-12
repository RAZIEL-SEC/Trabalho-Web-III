import type { CSSProperties } from 'react';

type IconName =
  | 'restaurant' | 'shopping_cart' | 'sanitizer' | 'school'
  | 'volunteer_activism' | 'handshake' | 'business' | 'mail'
  | 'smartphone' | 'location_on' | 'close' | 'menu'
  | 'dashboard' | 'swap_horiz' | 'add' | 'waving_hand'
  | 'search' | 'error' | 'target' | 'star' | 'arrow_forward'
  | 'check_circle' | 'inventory_2' | 'favorite' | 'checkroom' | 'linklist';

interface IconProps {
  name: IconName | 'instagram' | 'facebook' | 'linklist';
  className?: string;
  size?: number;
}

const brandPaths = {
  instagram: 'M7 2h10a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5H7a5 5 0 0 1-5-5V7a5 5 0 0 1 5-5Zm0 2A3 3 0 0 0 4 7v10a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V7a3 3 0 0 0-3-3H7Zm5 3a5 5 0 1 1 0 10 5 5 0 0 1 0-10Zm0 2a3 3 0 1 0 0 6 3 3 0 0 0 0-6Zm5.5-3a1.25 1.25 0 1 1 0 2.5 1.25 1.25 0 0 1 0-2.5Z',
  facebook: 'M13.5 22v-8h2.7l.4-3h-3.1V9.1c0-.9.3-1.5 1.6-1.5h1.7V4.9c-.3 0-1.3-.1-2.5-.1-2.5 0-4.2 1.5-4.2 4.3V11H7.3v3h2.8v8h3.4Z',
  linklist: 'M4 6a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3Zm0 4.5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3Zm0 4.5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3ZM8 6.5v2h13v-2H8Zm0 4.5v2h13v-2H8Zm0 4.5v2h13v-2H8Z'
};

export default function Icon({ name, className = '', size = 24 }: IconProps) {
  if (name === 'instagram' || name === 'facebook' || name === 'linklist') {
    return (
      <svg
        aria-hidden="true"
        className={className}
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill="currentColor"
        focusable="false"
      >
        <path d={brandPaths[name]} />
      </svg>
    );
  }

  const style = { fontSize: size } as CSSProperties;
  return (
    <span
      aria-hidden="true"
      className={`material-symbols-outlined ${className}`.trim()}
      style={style}
    >
      {name}
    </span>
  );
}
