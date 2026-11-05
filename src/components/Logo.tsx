interface LogoProps {
  size?: number;
}

export default function Logo({ size = 40 }: LogoProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Blue cap */}
      <ellipse cx="20" cy="22" rx="16" ry="7" fill="#2d7dd2" />
      {/* Cap top / crown */}
      <path d="M7 22 Q8 13 20 12 Q32 13 33 22Z" fill="#1a3a6e" />
      {/* Brim */}
      <rect x="4" y="21" width="24" height="3" rx="1.5" fill="#2d7dd2" />
      {/* Heart replacing 'o' */}
      <path d="M20 18 C20 18 17 15.5 17 14 C17 12.9 17.9 12 19 12 C19.6 12 20 12.4 20 12.4 C20 12.4 20.4 12 21 12 C22.1 12 23 12.9 23 14 C23 15.5 20 18 20 18Z" fill="#e83e5e" />
    </svg>
  );
}
