-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema thought_dashboard
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `thought_dashboard` ;

-- -----------------------------------------------------
-- Schema thought_dashboard
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `thought_dashboard` DEFAULT CHARACTER SET utf8 ;
USE `thought_dashboard` ;

-- -----------------------------------------------------
-- Table `thought_dashboard`.`users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `thought_dashboard`.`users` ;

CREATE TABLE IF NOT EXISTS `thought_dashboard`.`users` (
  `id_user` INT NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(45) NULL,
  `last_name` VARCHAR(45) NULL,
  `email` VARCHAR(45) NULL,
  `password` VARCHAR(255) NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  PRIMARY KEY (`id_user`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `thought_dashboard`.`thoughts`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `thought_dashboard`.`thoughts` ;

CREATE TABLE IF NOT EXISTS `thought_dashboard`.`thoughts` (
  `id_thought` INT NOT NULL AUTO_INCREMENT,
  `thought` VARCHAR(255) NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  `user_id` INT NOT NULL,
  PRIMARY KEY (`id_thought`),
  INDEX `fk_thoughts_users_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_thoughts_users`
    FOREIGN KEY (`user_id`)
    REFERENCES `thought_dashboard`.`users` (`id_user`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `thought_dashboard`.`users_thoughts`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `thought_dashboard`.`users_thoughts` ;

CREATE TABLE IF NOT EXISTS `thought_dashboard`.`users_thoughts` (
  `thoughts_id_thought` INT NOT NULL,
  `users_id_user` INT NOT NULL,
  PRIMARY KEY (`thoughts_id_thought`, `users_id_user`),
  INDEX `fk_thoughts_has_users_users1_idx` (`users_id_user` ASC) VISIBLE,
  INDEX `fk_thoughts_has_users_thoughts1_idx` (`thoughts_id_thought` ASC) VISIBLE,
  CONSTRAINT `fk_thoughts_has_users_thoughts1`
    FOREIGN KEY (`thoughts_id_thought`)
    REFERENCES `thought_dashboard`.`thoughts` (`id_thought`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_thoughts_has_users_users1`
    FOREIGN KEY (`users_id_user`)
    REFERENCES `thought_dashboard`.`users` (`id_user`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
