-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 13 Jun 2026 pada 17.02
-- Versi server: 10.4.32-MariaDB
-- Versi PHP: 8.2.12
SET SESSION sql_require_primary_key = 0;

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_kodim`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `riwayat_prediksi`
--
DROP TABLE IF EXISTS `riwayat_prediksi`;
CREATE TABLE `riwayat_prediksi` (
  `id` varchar(100) NOT NULL PRIMARY KEY,
  `nama` varchar(255) DEFAULT NULL,
  `umur` float DEFAULT NULL,
  `tb` float DEFAULT NULL,
  `bb` float DEFAULT NULL,
  `lari` float DEFAULT NULL,
  `pullup` float DEFAULT NULL,
  `situp` float DEFAULT NULL,
  `pushup` float DEFAULT NULL,
  `shuttle` float DEFAULT NULL,
  `hasil` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `riwayat_prediksi`
--

INSERT INTO `riwayat_prediksi` (`id`, `nama`, `umur`, `tb`, `bb`, `lari`, `pullup`, `situp`, `pushup`, `shuttle`, `hasil`) VALUES
('222', 'lulut', 22, 165, 65, 25000, 10, 45, 35, 17.5, 'BS'),
('224', 'lulut', 22, 165, 65, 25000, 10, 45, 35, 17.5, 'BS'),
('35', 'Agam', 22, 176, 65, 2500, 10, 10, 45, 16.6, 'C');

-- --------------------------------------------------------

--
-- Struktur dari tabel `users`
--
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) NOT NULL PRIMARY KEY,
  `username` varchar(50) DEFAULT NULL,
  `password` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `users`
--

INSERT INTO `users` (`id`, `username`, `password`) VALUES
(1, 'admin', 'admin123');

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `riwayat_prediksi`
--
-- ALTER TABLE `riwayat_prediksi`
--   ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `users`
--
-- ALTER TABLE `users`
--   ADD PRIMARY KEY (`id`),
--   ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
