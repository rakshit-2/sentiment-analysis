import { useEffect } from 'react';
import { ring } from 'ldrs';
import styles from './Loader.module.scss';

interface LoaderProps {
  size?: string;
  stroke?: string;
  speed?: string;
  color?: string;
  message?: string;
}

const Loader = ({ 
  size = "40", 
  stroke = "5", 
  speed = "2", 
  color = "black",
  message 
}: LoaderProps) => {
  useEffect(() => {
    ring.register();
  }, []);

  return (
    <div className={styles.loaderContainer}>
      <l-ring
        size={size}
        stroke={stroke}
        bg-opacity="0"
        speed={speed}
        color={color}
      ></l-ring>
      {message && <p className={styles.message}>{message}</p>}
    </div>
  );
};

export default Loader;
