require File.dirname(__FILE__) + "/../db.rb"

# Tags
Tag.create(:name => "red", :type => "color")
Tag.create(:name => "green", :type => "color")
Tag.create(:name => "large", :type => "dimensions")
Tag.create(:name => "small", :type => "dimensions")

# Products

# Gucci Handbag
product = Product.create(:name => "Gucci Handbag", :description => "awesome")
product.photos << Photo.create(:url => "http://guccigoods.com/wp-content/uploads/2008/03/authenticate_gucci_handbag.jpg", :width => 300, :height => 300)
product.photos << Photo.create(:url => "http://allwomenstalk.com/wp-content/uploads/2007/11/gucci41.jpg", :width => 400, :height => 400)
product.purchase_points << PurchasePoint.create(:name => "Gucci Web", :address => "www.gucci.com", :price => 1000000000.00) 
product.purchase_points << PurchasePoint.create(:name => "Gucci Awesome China Emporium", :address => "Beijing, China", :price => 10.00)
product.tags << Tag.first_or_create(:name => "red")
product.tags << Tag.first_or_create(:name => "large")
product.save

# Vuitton handbag
product = Product.create(:name => "Vuitton Handbag", :description => "great")
product.photos << Photo.create(:url => "http://www.icantwaittovote.org/blog/images/The%20Louis%20Vuitton%20Mahina%20XXL%20Handbag.jpg", :width => 440, :height => 304)
product.photos << Photo.create(:url => "http://2.bp.blogspot.com/_4_L4rYWKpoY/R54Brxx6AyI/AAAAAAAAANw/-eIKxxygljQ/s400/Louis_Vuitton_Handbags_LV_Bag.jpg", :width => 320, :height => 320)
product.purchase_points << PurchasePoint.create(:name => "Vuitton Manhattan", :address => "Manhattan, New York, NY", :price => 10.00)
product.tags << Tag.first_or_create(:name => "green")
product.tags << Tag.first_or_create(:name => "small")
product.save